How to make a better dbt

Performance:
  * Compile time is a bear
  * Doc creation time is a bear
    -> Don't make active database connections core
    -> Keep all compilation lightweight

Usability:
  * { ref(...) } syntax:
    -> Sucks that dbt files are not real SQL
    -> Hard to find where refs point to at times
    => Try https://github.com/macbre/sql-metadata
  
  * {{ config(...) }} syntax:
    -> Not as bad as ref stuff.. maybe keep if there's no better way

  * Extremely verbose yaml files everywhere
    -> Keep configuration to a minimum while being able to generate docs

  * Maybe co-opt database comments for documentation
  

TODO
1. Make a simple runner that builds a dag and runs it
2. Make a simple docs site from table comments