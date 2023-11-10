from django.db.models import F, OuterRef, Q, Subquery
from django.views.generic import ListView

from java_wallet.models import (
    Account,
    Block,
    IndirectIncoming,
    RewardRecipAssign,
    Transaction,
)
from scan.caching_paginator import CachingPaginator
from scan.helpers.queries import get_account_name
from scan.views.base import IntSlugDetailView
from scan.views.transactions import fill_data_transaction


class PoolListView(ListView):
    model = Block
    query = (
        Block.objects.using("java_wallet")
        .annotate(pool_id=Subquery(
            RewardRecipAssign.objects.using("java_wallet")
            .filter(~Q(recip_id=F('account_id')))
            .filter(account_id=OuterRef("generator_id"))
            .values("recip_id")[:1]
        ))
        .exclude(pool_id__isnull=True)
        .values("height")
        .filter(pool_id=OuterRef("recip_id"))
        .order_by("-height")
        .exclude(height__isnull=True)
        .filter(height__gt=1200000)
    )
    queryset = (
        RewardRecipAssign.objects.using("java_wallet")
        .filter(latest=1).filter(~Q(recip_id=F('account_id')))
        .annotate(block=query[:1])
        .values("recip_id", "block")
        .distinct()
        .exclude(block__isnull=True)
    )
    template_name = "pools/list.html"
    context_object_name = "pools"
    paginator_class = CachingPaginator
    paginate_by = 25
    ordering = "-block"


class PoolDetailView(IntSlugDetailView):
    model = Account
    queryset = Account.objects.using("java_wallet").filter(latest=True).all()
    template_name = "pools/detail.html"
    context_object_name = "address"
    slug_field = "id"
    slug_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context[self.context_object_name]

        # To also show contract names when checking as an account
        if not obj.name:
            obj.name = get_account_name(obj.id)

        # transactions
        indirects_query = (
            IndirectIncoming.objects.using("java_wallet")
            .values_list('transaction_id', flat=True)
            .filter(account_id=obj.id)
        )
        indirects_count = indirects_query.count()

        txs_query = (
            Transaction.objects.using("java_wallet")
            .filter(Q(sender_id=obj.id) | Q(recipient_id=obj.id))
        )
        txs_cnt = txs_query.count() + indirects_count

        if indirects_count > 0:
            txs_indirects = (
                Transaction.objects.using("java_wallet")
                .filter(id__in=indirects_query)
            )
            txs_query = txs_query.union(txs_indirects)

        txs = txs_query.order_by("-height")[:min(txs_cnt, 15)]

        for t in txs:
            fill_data_transaction(t, list_page=True)

        context["txs"] = txs
        context["txs_cnt"] = txs_cnt

        # Miners

        miners_query = (
            RewardRecipAssign.objects.using("java_wallet")
            .filter(recip_id=obj.id, latest=1)
        )

        miners = miners_query.order_by('-height')
        miners_cnt = miners_query.count()

        context["miners"] = miners[:25]
        context["miners_cnt"] = miners_cnt

        return context
