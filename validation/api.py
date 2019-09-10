import json

from confluent_kafka import Producer
from django.conf import settings

from validation import OUT_TOPIC


def request_asset_validation(modeladmin, request, queryset):
    """
    Send a request to kafka to validate every asset params in queryset
    :param queryset:
    """
    p = Producer({'bootstrap.servers': f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}'})
    for a in queryset:
        p.poll(0)
        data = json.dumps({
            'node': 'https://main-node.jwallet.network/',
            'uuid': str(a.uuid),
            'address': a.address,
            'staticGasAmount': a.properties.get('static_gas_amount'),
            'deploymentBlockNumber': a.properties.get('deployment_block'),
        })

        p.produce(OUT_TOPIC, data)

    p.flush()


request_asset_validation.short_description = 'Validate asset'
