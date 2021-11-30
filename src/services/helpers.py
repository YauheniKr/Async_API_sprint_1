def get_pagination_param(page_number: int, size: int) -> tuple:
    start_number = (page_number - 1) * size
    end_number = page_number * size
    return start_number, end_number
