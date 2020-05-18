
from django.conf import settings
from django.core import validators
from django.utils.deconstruct import deconstructible

from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.settings import api_settings

"""
xxxxxx yyyy MM dd 375 0     十八位
地区： [1-9]\d{5}
年的前两位： (19|([29]\d))            1900-2999
年的后两位： \d{2}
月份： ((0[1-9])|(10|11|12))
天数： (([0-2][1-9])|10|20|30|31)          闰年不能禁止29+
三位顺序码： \d{3}
两位顺序码： \d{2}
校验码： [0-9Xx]
"""
ID_EXP_18 = r'^[1-9]\d{5}(19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$'

@deconstructible
class IDValidator(validators.RegexValidator):
    regex = ID_EXP_18
    message = '无效的身份证号码。'
    flags = 0

"""
验证是否为有效手机号码, 支持号码：
移动：134，135，136，137，138，139，147，150，151，152，157，158，159，178，182，183，184，187，188，198
联通：130，131，132，145，155，156，166，176，185，186
电信：133，153，173，177，180，181，189，199
"""
MOBILE_EXP = r'^1((3[\d])|(4[75])|(5[^3|4])|(66)|(7[3678])|(8[\d])|(9[89]))\d{8}$'

@deconstructible
class MobileValidator(validators.RegexValidator):
    regex = MOBILE_EXP
    message = '无效的手机号码。'
    flags = 0
    
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
    page_size = 10
    #可以通过传入../?page=xx&size=xx,改变默认每页显示的个数
    page_size_query_param = "size"
    #最大页数不超过100
    max_page_size = 100
    #获取页码数的
    page_query_param = "page"

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
        if response['code'] >= 777: 
            return Response(response, status=500)
        return Response(response, status=exc.status_code)

