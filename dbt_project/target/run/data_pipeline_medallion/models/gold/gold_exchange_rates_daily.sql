
  
    

create or replace transient table DE_PORTOFOLIO_DB.RAW_gold.gold_exchange_rates_daily
    
    
    
    
    

    as (with silver as (

    select * from DE_PORTOFOLIO_DB.RAW_staging.silver_exchange_rates

),

with_previous as (

    select
        base_currency,
        target_currency,
        rate,
        rate_date,
        lag(rate) over (
            partition by base_currency, target_currency
            order by rate_date
        ) as previous_rate
    
    from silver
)

select
    base_currency,
    target_currency,
    rate,
    rate_date,
    previous_rate,
    round(
        case
            when previous_rate is not null and previous_rate != 0
            then (rate - previous_rate) / previous_rate * 100
            else null
        end,
        4
    ) as rate_change_pct

from with_previous
    )
;


  