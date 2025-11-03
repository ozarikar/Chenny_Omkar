from typing import Tuple, List, Union
from .loader import Loader
from .table_support import get_table_select_sql, WhereBase


class LimitExec:
	
	def __init__(self, _exec, table_name: str, order_by: str, limit: Union[int, Tuple[int], List[int]]):
		self.exec = _exec
		self.table = table_name
		self.order_by = order_by
		self.limit = limit
	
	def select(self, *columns) -> List[Tuple]:
		"""
		Select data from table and return list results(tuple).

		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').limit(1).select('id', 'name', 'age')
		[(3, '张三', 20)]
		"""
		sql = get_table_select_sql(self.table, None, self.order_by, self.limit, *columns)
		if isinstance(self.limit, int):
			return self.exec.do_select(sql, self.limit)
		return self.exec.do_select(sql, *self.limit)
	
	def query(self, *columns) -> List[Tuple]:
		"""
		Select data from table and return list results(dict).

		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').limit(1).query('id', 'name', 'age')
		[{'id': 3, 'name': '张三', 'age': 20}]
		"""
		sql = get_table_select_sql(self.table, None, self.order_by, self.limit, *columns)
		if isinstance(self.limit, int):
			return self.exec.do_query(sql, self.limit)
		else:
			return self.exec.do_query(sql, *self.limit)
	
	def ravel_list(self, column: str) -> List:
		"""
		Select data from table and return list results.

		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').limit(3).ravel_list('name')
		['张三', '李四', '王五']
		"""
		sql = get_table_select_sql(self.table, None, self.order_by, self.limit, column)
		if isinstance(self.limit, int):
			return self.exec.do_ravel_list(sql, self.limit)
		return self.exec.do_ravel_list(sql, *self.limit)

	def load(self, *columns) -> Loader:
		"""
		Select page data from table and return a Loader instance
		
		:return: Loader
		
		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').limit(1).load('id', 'name', 'age')
		Lodder()
		"""
		sql = get_table_select_sql(self.table, None, self.order_by, self.limit, *columns)
		if isinstance(self.limit, int):
			return self.exec.do_load(sql, self.limit)
		else:
			return self.exec.do_load(sql, *self.limit)


class ColumnLimitExec:
	
	def __init__(self, limit_exec: LimitExec, *columns):
		self.limit_exec = limit_exec
		self.columns = columns
	
	def select(self) -> List[Tuple]:
		"""
		Select data from table and return list results(tuple).

		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').columns('id', 'name', 'age').limit(1).select()
		[(3, '张三', 20)]
		"""
		return self.limit_exec.select(*self.columns)
	
	def query(self) -> List[Tuple]:
		"""
		Select data from table and return list results(dict).

		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').columns('id', 'name', 'age').limit(1).query()
		[{'id': 3, 'name': '张三', 'age': 20}]
		"""
		return self.limit_exec.query(*self.columns)
	
	def ravel_list(self) -> List:
		"""
		Select data from table and return list.

		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').columns('name').limit(3).ravel_list()
		['张三', '李四', '王五']
		"""
		return self.limit_exec.ravel_list(*self.columns)
	
	def to_df(self):
		"""
		Select from table and return pandas DataFrame instance.
		
		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').columns('id', 'name', 'age').limit(10).to_df()
		"""
		return self.limit_exec.load(*self.columns).to_df()
	
	def to_pl(self):
		"""
		Select from table and return polars DataFrame instance.
		
		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').columns('id', 'name', 'age').limit(10).to_pl()
		"""
		return self.limit_exec.load(*self.columns).to_pl()

	def to_csv(self, file_name: str, delimiter=',', header=True, encoding='utf-8'):
		"""
		Select from table and sava as a csv file.
		
		Examples
		--------
		>>> import sqlexecx as db
		>>> db..table('person').columns('id', 'name', 'age').limit(10).to_csv('test.csv')
		"""
		self.limit_exec.load(*self.columns).to_csv(file_name, delimiter, header, encoding)

	def to_json(self, file_name: str, encoding='utf-8'):
		"""
		Select from table and sava as a json file.
		
		Examples
		--------
		>>> import sqlexecx as db
		>>> db..table('person').columns('id', 'name', 'age').limit(10).to_json('test.json')
		"""
		self.limit_exec.load(*self.columns).to_json(file_name, encoding)
	
	
class WhereLimitExec(WhereBase):

	def __init__(self, _exec, table_name: str, order_by: str, limit: Union[int, Tuple[int], List[int]], **kwargs):
		super().__init__(_exec, table_name, order_by, **kwargs)
		self.limit_ = limit
		
		
class ColumnWhereLimitExec:
	
	def __init__(self, where_limit_exec: WhereLimitExec, *columns):
		self.where_limit_exec = where_limit_exec
		self.columns = columns
	
	def select(self) -> List[Tuple]:
		"""
		Select data from table and return list results(tuple).

		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20).limit(1).select()
		[(3, '张三', 20)]
		"""
		return self.where_limit_exec.select(*self.columns)

	def query(self) -> List[dict]:
		"""
		Select data from table and return list results(dict).
		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20).limit(1).query()
		[{'id': 3, 'name': '张三', 'age': 20}]
		"""
		return self.where_limit_exec.query(*self.columns)
	
	def ravel_list(self) -> List:
		"""
		Select data from table and return list.

		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').columns('name').where(age=20).limit(3).ravel_list()
		['张三', '李四', '王五']
		"""
		return self.where_limit_exec.ravel_list(*self.columns)

	def to_df(self):
		"""
		Select from table and return pandas DataFrame instance.
		
		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20).limit(10).to_df()
		"""
		return self.where_limit_exec.load(*self.columns).to_df()

	def to_pl(self):
		"""
		Select from table and return polars DataFrame instance.
		
		Examples
		--------
		>>> import sqlexecx as db
		>>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20).limit(10).to_pl()
		"""
		return self.where_limit_exec.load(*self.columns).to_pl()

	def to_csv(self, file_name: str, delimiter=',', header=True, encoding='utf-8'):
		"""
		Select from table and sava as a csv file.
		
		Examples
		--------
		>>> import sqlexecx as db
		>>> db..table('person').columns('id', 'name', 'age').where(name='张三', age=20).limit(10).to_csv('test.csv')
		"""
		self.where_limit_exec.load(*self.columns).to_csv(file_name, delimiter, header, encoding)

	def to_json(self, file_name: str, encoding='utf-8'):
		"""
		Select from table and sava as a json file.
		
		Examples
		--------
		>>> import sqlexecx as db
		>>> db..table('person').columns('id', 'name', 'age').where(name='张三', age=20).limit(10).to_json('test.json')
		"""
		self.where_limit_exec.load(*self.columns).to_json(file_name, encoding)
