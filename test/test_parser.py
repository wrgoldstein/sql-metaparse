from sql_metaparse import parse_meta
import string

wm = whitespace_map = dict.fromkeys(ord(c) for c in string.whitespace)


def test_parse_tables():
    q = "select * from foo"
    assert parse_meta(q)['tables'] == ['"foo"']

    q = "select * from foo,bar"
    assert parse_meta(q)['tables'] == ['"foo"', '"bar"']

    q = 'select abc as 123 from "table"'
    assert parse_meta(q)['tables'] == ['"table"']

    q = """
    with temp as (
        select abc,
            def,
            feg as hij
        from (
            select * from people
        ) as outer_people
        left join other on people.id=other.id
        inner join blah aliasblah on people.id=blah.id
    ),
    nasty as (
        select 123 from "prod".foo
        union all
        select 455 from clean."gymnastics" "gym" 
        limit 500
    )
    select * from temp, nasty, omg3
    where blizzard = 'never'
    """

    assert parse_meta(q)['tables'] == ['"people"', '"other"', '"blah"', '"prod"."foo"', '"clean"."gymnastics"', '"omg3"']


def test_parse_columns():
    q = """
    select id,
        -- we use hometown to track people down and peek in their living room windows
        hometown,
        case when (a and b)
            then true
        end as "that was a case statement",
        -- if we group people by favorite snack we can predict their astrological sign
        favorite_snack as astro_picker,
        -- obviously its super convenient to get people's futures
        -- for which a crystal ball is handy
        crystal_ball.future,
        nullif(json_extract_path_text(raw_data, 'EventType', true), '') as extracted
    from people
    left join crystal_ball
        on people.fortune_id = crystal_ball.id
    """
    meta = parse_meta(q)
    assert meta['tables'] == ['"people"', '"crystal_ball"']

    columns = meta['columns']

    assert columns[0][0] == columns[0][1] == 'id'
    assert columns[0][2] is None

    assert columns[1][0] == "hometown"
    assert columns[1][2] == "we use hometown to track people down and peek in their living room windows"

    assert columns[2][1] == '"that was a case statement"'

    assert columns[3][1] == "astro_picker"
    assert columns[3][2] == "if we group people by favorite snack we can predict their astrological sign"

    assert columns[4][2].split("\n")[0] == "obviously its super convenient to get people's futures"
    assert columns[4][2].split("\n")[1] == "for which a crystal ball is handy"

    print(columns[5])
    assert columns[5][0] == "nullif (json_extract_path_text (raw_data, 'EventType', true),\n        '') as extracted"
    assert columns[5][1] == "extracted"


def test_window_functions():
    q = """
    with valid_transitions as (
    select distinct
        transition_id
        ,first_value(account_id) over (partition by transition_id order by created_at
            rows between unbounded preceding and unbounded following) as account_id
        ,activity_id
        ,first_value(created_at) over (partition by transition_id order by created_at
            rows between unbounded preceding and unbounded following) as created_at
        ,first_value(from_status) over (partition by transition_id order by created_at
            rows between unbounded preceding and unbounded following) as from_status
        ,first_value(to_status) over (partition by transition_id order by created_at
            rows between unbounded preceding and unbounded following) as to_status
    from activity_status_transition_detail
)
select
    transition_id
    ,activity_id
    ,lead(account_id,1) over (partition by activity_id order by created_at) as account_id
    ,to_status as status
    ,created_at
    ,lead(to_status) over (partition by activity_id order by created_at) as next_status
    ,lead(created_at)  over (partition by activity_id order by  created_at) as next_status_at
    ,row_number() over (partition by activity_id order by  created_at) as activity_sequence
    ,date_diff('seconds', created_at :: timestamp, coalesce(next_status_at, getdate()) :: timestamp) as seconds_in_status
from valid_transitions
"""
    meta = parse_meta(q)
    assert meta['tables'] == ['"activity_status_transition_detail"']
    columns = meta['columns']
    assert len(columns) == 9
    assert columns[5][1] == "next_status"
    assert columns[5][0].translate(wm) == "lead(to_status) over (partition by activity_id order by created_at) as next_status".translate(wm)
