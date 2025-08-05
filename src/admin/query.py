from tortoise.transactions import in_transaction


async def aggregate_by_time_slice(unit: str = "minute", interval: int = 10):
    async with in_transaction() as conn:
        if unit == "minute":
            time_slice_expr = f"DATE_TRUNC('minute', s.timestamp) - (EXTRACT(MINUTE FROM s.timestamp)::INT % {interval}) * INTERVAL '1 minute'"
        elif unit == "hour":
            time_slice_expr = f"DATE_TRUNC('hour', s.timestamp) - (EXTRACT(HOUR FROM s.timestamp)::INT % {interval}) * INTERVAL '1 hour'"
        query = f"""
        SELECT 
            d.app_name as microservice,
            d.name AS dependency_name,
            {time_slice_expr} as time_slice,
            AVG(s.latency) AS latency,
            AVG(s.response_time) AS response_time,
            AVG(s.rtt) AS rtt,
            AVG(s.availability) AS availability,
            AVG(s.cpu) as cpu,
            AVG(s.memory) as memory,
            COUNT(*) AS throughput
        FROM sla_report s
        JOIN dependencies d ON s.dependency_id = d.id
        GROUP BY d.app_name, d.name, time_slice
        ORDER BY time_slice DESC, d.app_name, d.name;
        """

        rows = await conn.execute_query_dict(query)
        return rows


async def aggregate_metrics():
    async with in_transaction() as conn:
        query = f"""
        SELECT 
            d.app_name as microservice,
            d.name AS dependence_name,
            AVG(s.latency) AS latency,
            AVG(s.response_time) AS response_time,
            AVG(s.rtt) AS rtt,
            AVG(s.availability) AS availability,
            AVG(s.cpu) as cpu,
            AVG(s.memory) as memory,
            COUNT(*) AS throughput
        FROM sla_report s
        JOIN dependencies d ON s.dependency_id = d.id
        GROUP BY d.app_name, d.name
        ORDER BY d.name;
        """

        rows = await conn.execute_query_dict(query)
        return rows
