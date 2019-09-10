
from confluent_kafka.cimpl import Consumer
from django.http import HttpResponse
from django.conf import settings

from validation import IN_TOPIC


def check_validation_results(request):
    """
    Check asset validation results
    """
    c = Consumer({
        'bootstrap.servers': f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}',
        'group.id': 'mygroup',
        'auto.offset.reset': 'earliest'
    })

    c.subscribe([IN_TOPIC])
    msg = c.poll(15.0)

    if msg is None:
        result = 'No new results'
    else:
        if msg.error():
            result = f'Error: {msg.error()}'
        else:
            result = msg.value().decode('utf-8')

    c.close()

    return HttpResponse(result, content_type="application/json")
