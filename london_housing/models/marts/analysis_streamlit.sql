-- top 3 rising
select
    district,
    county,
    avg_price,
    mom_change_pct,
    transaction_count
from fct_price_index
where
    transfer_month = '2023-03-01'
    and transaction_count >= 20
order by mom_change_pct desc
limit 3


-- bottom 3 falling
select
    district,
    county,
    avg_price,
    mom_change_pct,
    transaction_count
from fct_price_index
where
    transfer_month = '2023-03-01'
    and transaction_count >= 20
order by mom_change_pct asc
limit 3