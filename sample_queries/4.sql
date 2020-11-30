select
	o_orderpriority,
	count(*) as order_count
from
	orders
where
	o_totalprice > 100000
	and exists (
		select
			*
		from
			lineitem
		where
			l_orderkey = o_orderkey
			
	)
group by
	o_orderpriority
order by
	o_orderpriority