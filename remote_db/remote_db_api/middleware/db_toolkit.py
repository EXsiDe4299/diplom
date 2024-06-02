db_toolkit_data = {'mssql': {'account_type_id': 1,
                             'database_type_id': 1,
                             'create_user_query': lambda account_login,
                                                         user_password: f"USE master;\nCREATE LOGIN {account_login} WITH PASSWORD='{user_password}';\n\nALTER SERVER ROLE dbcreator ADD MEMBER {account_login};\nUSE master;\nGRANT CREATE ANY DATABASE TO {account_login};",

                             'edit_login_query': lambda user_login,
                                                        new_account_login: f"ALTER LOGIN {user_login} WITH NAME = {new_account_login};",
                             'edit_password_query': lambda new_account_login,
                                                           new_account_password: f"ALTER LOGIN {new_account_login} WITH PASSWORD = '{new_account_password}';",

                             'create_database_query': lambda database_name, account_login: [
                                 f'CREATE DATABASE {database_name};',
                                 f'USE {database_name};\nCREATE USER {account_login} FOR LOGIN {account_login}'],
                             'select_version_query': 'SELECT @@VERSION',
                             'delete_database_query': lambda
                                 database_name: f'USE master;\nALTER DATABASE {database_name} SET SINGLE_USER WITH ROLLBACK IMMEDIATE;\nDROP DATABASE {database_name};'},
                   'postgresql': {'account_type_id': 2,
                                  'database_type_id': 2,
                                  'create_user_query': lambda account_login,
                                                              user_password: f"CREATE USER {account_login} WITH PASSWORD '{user_password}' CREATEDB;",

                                  'edit_login_query': lambda user_login,
                                                             new_account_login: f"ALTER USER {user_login} RENAME TO {new_account_login};",
                                  'edit_password_query': lambda new_account_login,
                                                                new_account_password: f"ALTER USER {new_account_login} WITH PASSWORD '{new_account_password}';",

                                  'create_database_query': lambda database_name, account_login: [
                                      f'CREATE DATABASE {database_name} OWNER {account_login};'],
                                  'select_version_query': 'SELECT version()',
                                  'delete_database_query': lambda
                                      database_name: f'DROP DATABASE {database_name} WITH (FORCE);'},
                   'mysql': {'account_type_id': 3,
                             'database_type_id': 3,
                             'create_user_query': lambda account_login,
                                                         user_password: f"CREATE USER '{account_login}'@localhost IDENTIFIED BY '{user_password}';",

                             'edit_login_query': lambda user_login,
                                                        new_account_login: f"RENAME USER '{user_login}'@'localhost' TO '{new_account_login}'@'localhost';",
                             'edit_password_query': lambda new_account_login,
                                                           new_account_password: f"SET PASSWORD FOR '{new_account_login}'@'localhost' = PASSWORD('{new_account_password}');",

                             'create_database_query': lambda database_name,
                                                             account_login: [f'CREATE DATABASE {database_name};',
                                                                             f'GRANT ALL PRIVILEGES ON {database_name}.* TO {account_login}@localhost;'],
                             'select_version_query': 'SELECT @@version',
                             'delete_database_query': lambda database_name: f'DROP DATABASE {database_name};'}}
