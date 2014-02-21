drop table if exists system_type;
create table system_type(
   id integer primary key autoincrement,
   test_field text not null,
   field_desc text not null
);
