from tortoise.transactions import in_transaction


async def aggregate_by_time_slice(minutes: int):
    async with in_transaction() as conn:
        query = f"""
        SELECT 
            d.name AS dependency_name,
            DATE_TRUNC('minute', s.timestamp) - (EXTRACT(MINUTE FROM s.timestamp)::INT % {minutes}) * INTERVAL '1 minute' as time_slice,
            AVG(s.latency) AS latency,
            AVG(s.response_time) AS response_time,
            AVG(s.rtt) AS rtt,
            AVG(s.availability) AS availability,
            AVG(s.cpu) as cpu,
            AVG(s.memory) as memory,
            COUNT(*) AS throughput
        FROM sla_report s
        JOIN dependencies d ON s.dependency_id = d.id
        GROUP BY d.name, time_slice
        ORDER BY time_slice DESC, d.name;
        """

        rows = await conn.execute_query_dict(query)
        return rows
