
def get_page_start(page_num: int, page_size: int) -> int:
	assert page_num >= 1 and page_size >= 1, "'page_num' and 'page_size' should be higher or equal to 1"
	return (page_num - 1) * page_size
