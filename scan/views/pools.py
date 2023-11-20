import pandas as pd
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
from scan.helpers.queries import (
    get_account_name,
    get_count_of_miners,
    get_description_url,
    get_forged_blocks_of_pool,
    get_timestamp_of_block,
)
from scan.views.base import IntSlugDetailView
from scan.views.transactions import fill_data_transaction

BLOCKS_OF_HALFYEAR = 65700


def fill_data_pool(pool):
    pool["url"] = get_description_url(pool["pool_id"])
    pool["miners_cnt"] = get_count_of_miners(pool["pool_id"])
    pool["block_timestamp"] = get_timestamp_of_block(pool["block"])


class PoolListView(ListView):
    model = Block
    queryset = (
        Block.objects.using("java_wallet")
        .annotate(block=F("height"))
        .annotate(
            pool_id=RewardRecipAssign.objects.using("java_wallet")
            .filter(height__lte=OuterRef("height"))
            .filter(account_id=OuterRef("generator_id"))
            .order_by("-height")
            .values("recip_id")
            [:1]
        )
        .values("block", "pool_id")
        .filter(~Q(pool_id=F('generator_id')))
    )
    template_name = "pools/list.html"
    context_object_name = "pools"
    paginator_class = CachingPaginator
    paginate_by = 25
    ordering = "-block"

    def get_queryset(self):
        last_block = (
            Block.objects.using("java_wallet")
            .values_list("height", flat=True)
            .order_by("-height")
            .first()
        )
        since_block = last_block - BLOCKS_OF_HALFYEAR
        qs = self.queryset.filter(block__gte=since_block).order_by("-block")
        qs_data = pd.DataFrame.from_records(qs)
        data = qs_data.groupby('pool_id').first().sort_values(by='block', ascending=False)
        pool_s_last_forged_blocks = []
        for index, row in data.iterrows():
            pool_s_last_forged_blocks.append(row["block"])
        return qs.filter(block__in=pool_s_last_forged_blocks).order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context[self.context_object_name]

        for pool in obj:
            fill_data_pool(pool)
        return context


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
            .filter(~Q(recip_id=F('account_id')))
            .filter(recip_id=obj.id)
            .filter(latest=1)
            .values("recip_id", "account_id", "height")
        )

        miners = miners_query.order_by('-height')

        miners = miners[:25]
        for miner in miners:
            miner["block_timestamp"] = get_timestamp_of_block(miner["height"])

        context["miners"] = miners
        context["miners_cnt"] = get_count_of_miners(obj.id)

        # Forged blocks

        forged_blocks = get_forged_blocks_of_pool(obj.id)
        forged_blocks_cnt = forged_blocks.count()
        forged_blocks = forged_blocks[:25]
        for forged_block in forged_blocks:
            forged_block["block_timestamp"] = get_timestamp_of_block(forged_block["block"])

        context["forged_blocks"] = forged_blocks
        context["forged_blocks_cnt"] = forged_blocks_cnt

        return context
