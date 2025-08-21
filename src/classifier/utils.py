from src.models import Sla


async def get_sla_values():
    async def get_threshold(lookup: str):
        sla = await Sla.get_or_none(metric__name__icontains=lookup)
        return sla.max_threshold if sla else None

    return {
        "cpu": await get_threshold("cpu"),
        "mem": await get_threshold("memoria"),
        "avail": await get_threshold("disponibilidade"),
        "response_time": await get_threshold("tempo de resposta"),
        "latency": await get_threshold("latencia"),
        "rtt": await get_threshold("rtt"),
    }


def classify_full_metrics(row: dict, sla: dict):
    cpu = row.get("cpu_usage")
    mem = row.get("memory_usage")
    avail = row.get("availability")
    resp = row.get("response_time")

    # ➤ Categoria 2 – Anômalo
    if cpu > 100 or mem > 100 or avail <= 0.0 or resp > 60:
        return 2

    # ➤ Categoria 1 – Instável
    print(
        cpu > sla.get("cpu"),
        mem > sla.get("mem"),
        avail,
        sla.get("avail"),
        resp > sla.get("response_time"),
    )
    if (
        cpu > sla.get("cpu")
        or mem > sla.get("mem")
        or avail * 100 < sla.get("avail")
        or resp > sla.get("response_time")
    ):
        return 1

    # ➤ Categoria 0 – Operacional
    return 0
