
from django.conf import settings

from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_jwt.settings import api_settings

#APIView异常处理函数
def handle_api_exception(exc):
    if not isinstance(exc, exceptions.APIException):
        if settings.DEBUG:
            print('Exception type:', type(exc))
            print('args:', exc.args)
        return {'code': 777, 
                'field': 'non_field_errors',
                'message': '未知原因的错误。'}

    if settings.DEBUG:
        print('args:', exc.args)
        print('default_code:', exc.default_code)
        print('default_detail:', exc.default_detail)
        print('get_codes:', exc.get_codes())
        print('get_full_details:', exc.get_full_details())
        print('status_code:', exc.status_code)

    if exc.default_code == 'invalid':
        field, code = exc.get_codes().popitem()
        response = {'field': field, 'message': exc.args[0][field][0]}
        if code[0] == 'unique': # 唯一性冲突
            response['code'] = 701
        elif code[0] == 'required': # 缺失关键参数
            response['code'] = 702
        elif code[0] == 'disabled': # user account is disabled
            response['code'] = 703
        elif code[0] == 'disaccord': # 一致性错误
            response['code'] = 704
        else: #if code in ('does_not_exit', 'null', 'incorrect_type'): #无效的参数
            response['code'] = 705
    else:
        response = {'code': exc.status_code, 
                    'field': 'non_field_errors', 
                    'message': exc.default_detail}
    return response

class PublicPagination(api_settings.DEFAULT_PAGINATION_CLASS):
    #每页显示多少个
    #page_size = 10
    #默认每页显示3个，可以通过传入pager1/?page=2&size=4,改变默认每页显示的个数
    page_size_query_param = "size"
    #最大页数不超过100
    max_page_size = 100
    #获取页码数的
    #page_query_param = "page"

class PublicView(APIView):
    pagination_class = PublicPagination

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def handle_exception(self, exc):
        response = handle_api_exception(exc)
        if response['code'] == 777:
            return response(response, status=777)
        return Response(response, status=exc.status_code)

