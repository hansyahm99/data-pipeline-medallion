with staged as (

    select * from {{ ref('stg_exchange_rates') }}
),

filtered as (

    select * from staged
    where rate is not null
        and rate > 0
),

deduped as (

    select
        base_currency,
        target_currency,
        rate,
        rate_date,
        ingested_at,
        source_file,
        row_number() over (
            partition by base_currency, target_currency, rate_date
            order by ingested_at desc
        ) as row_num
    
    from filtered
)

select
    base_currency,
    target_currency,
    rate,
    rate_date,
    ingested_at,
    source_file
from deduped
where row_num = 1