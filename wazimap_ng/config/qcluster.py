import os
from wazimap_ng.utils import int_or_none, truthy


class QCluster:
    # Q_CLUSTER = {
    #        "orm": 'default',
    #        "retry": int(os.environ.get("Q_CLUSTER_RETRY", 100000)),
    #        "workers": int(os.environ.get("Q_CLUSTER_WORKERS", 4)),
    #        "recycle": int(os.environ.get("Q_CLUSTER_RECYCLE", 500)),
    #        "timeout": int_or_none(os.environ.get("Q_CLUSTER_TIMEOUT", None)),
    #        "ack_failures": truthy(os.environ.get("Q_CLUSTER_ACK_FAILURES", True)),
    #        "sync": truthy(os.environ.get("Q_CLUSTER_SYNC", False)),
    # }

    Q_CLUSTER = {
        "redis": os.environ.get("REDIS_URL"),
        "workers": int(os.environ.get("Q_CLUSTER_WORKERS", 4)),
        "recycle": int(os.environ.get("Q_CLUSTER_RECYCLE", 10)),
    }
