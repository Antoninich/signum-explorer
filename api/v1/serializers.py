from datetime import datetime

from rest_framework.serializers import IntegerField, Serializer, SerializerMethodField

from burst.constants import BLOCK_CHAIN_START_AT, TxSubtypePayment


class PendingTxsSerializer(Serializer):
    type = IntegerField(read_only=True)
    subtype = IntegerField(read_only=True)
    timestamp = SerializerMethodField(read_only=True)
    amountNQT = IntegerField(read_only=True)
    feeNQT = IntegerField(read_only=True)
    sender = IntegerField(read_only=True)
    recipient = IntegerField(read_only=True)
    recipients = SerializerMethodField(read_only=True)

    @staticmethod
    def get_timestamp(data):
        return datetime.fromtimestamp(data["timestamp"] + BLOCK_CHAIN_START_AT)

    @staticmethod
    def get_recipients(data):
        result = []

        if data["subtype"] == TxSubtypePayment.MULTI_OUT:
            for x in data["attachment"]["recipients"]:
                result.append({"address": int(x[0]), "amount": int(x[1])})

        elif data["subtype"] == TxSubtypePayment.MULTI_OUT_SAME:
            amount = int(data["amountNQT"]) / len(data["attachment"]["recipients"])
            for x in data["attachment"]["recipients"]:
                result.append({"address": int(x), "amount": amount})

        return result or None

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
