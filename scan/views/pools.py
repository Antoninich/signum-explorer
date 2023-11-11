from django.db.models import F, OuterRef, Q
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
    model = RewardRecipAssign
    queryset = (
        RewardRecipAssign.objects.using("java_wallet")
        .filter(~Q(recip_id=F('account_id')))
        .values("recip_id", "account_id")
    )
    template_name = "pools/list.html"
    context_object_name = "pools"
    paginator_class = CachingPaginator
    paginate_by = 25
    ordering = "-block"

    def get_queryset(self):
        qs = self.queryset
        query_block = (
            Block.objects.using("java_wallet")
            .values("generator_id", "height")
            .all()
        )
        query_forged_block_and_pool_id = (
            query_block
            .annotate(
                pool_id=qs
                .filter(height__lte=OuterRef("height"))
                .filter(account_id=OuterRef("generator_id"))
                .order_by("-height")
                .values("recip_id")
                [:1]
            )
            .order_by("-height")
            .values("pool_id", "height")
            .exclude(height__isnull=True)
            .exclude(pool_id__isnull=True)
        )

        pool_s_last_forged_blocks = []
        pools_list = []
        for query in query_forged_block_and_pool_id:
            if query["pool_id"] not in pools_list:
                pool_s_last_forged_blocks.append(query["height"])
                pools_list.append(query["pool_id"])

        return (
            query_forged_block_and_pool_id
            .filter(height__in=pool_s_last_forged_blocks)
        )


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
