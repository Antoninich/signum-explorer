from django.db.models import F, Q
from django.views.generic import ListView

from scan.helpers.queries import get_timestamp_of_block
from scan.models import Pool


class ForgedBlocksListView(ListView):
    model = Pool
    queryset = (
        Pool.objects
        .order_by("-block")
        .filter(~Q(pool_id=F("generator_id")))
        .values("block", "generator_id")
    )
    template_name = "forged_blocks/list.html"
    context_object_name = "forged_blocks"
    paginate_by = 25
    ordering = "-block"

    def get_queryset(self):
        qs = self.queryset
        if 'a' in self.request.GET:
            qs = qs.filter(pool_id=self.request.GET['a'])
        return qs.order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context[self.context_object_name]
        for forged_block in obj:
            forged_block["block_timestamp"] = get_timestamp_of_block(forged_block["block"])
        return context
