# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from python_atom_sdk.setting import BK_ATOM_STATUS

import python_atom_sdk as sdk
from .error_code import ErrorCode

import json
import requests

err_code = ErrorCode()


def exit_with_error(error_type=None, error_code=None, error_msg="failed"):
    """
    @summary: exit with error
    """
    if not error_type:
        error_type = sdk.OutputErrorType.PLUGIN
    if not error_code:
        error_code = err_code.PLUGIN_ERROR
    sdk.log.error("error_type: {}, error_code: {}, error_msg: {}".format(error_type, error_code, error_msg))

    output_data = {
        "status":    sdk.status.FAILURE,
        "errorType": error_type,
        "errorCode": error_code,
        "message":   error_msg,
        "type":      sdk.output_template_type.DEFAULT
    }
    sdk.set_output(output_data)

    exit(error_code)


def exit_with_succ(data=None, quality_data=None, msg="run succ"):
    """
    @summary: exit with succ
    """
    if not data:
        data = {}

    output_template = sdk.output_template_type.DEFAULT
    if quality_data:
        output_template = sdk.output_template_type.QUALITY

    output_data = {
        "status":  sdk.status.SUCCESS,
        "message": msg,
        "type":    output_template,
        "data":    data
    }

    if quality_data:
        output_data["qualityData"] = quality_data

    sdk.set_output(output_data)

    sdk.log.info("finish")
    exit(err_code.OK)


def main():
    """
    @summary: main
    """
    sdk.log.info("enter main")

    # 输入
    input_params = sdk.get_input()

    # 获取名为input_demo的输入字段值
    send_to = input_params.get("send_to", None)
    sdk.log.info("send_to is {}".format(send_to))

    if not send_to:
        exit_with_error(error_type=sdk.output_error_type.USER,
                        error_code=err_code.USER_CONFIG_ERROR,
                        error_msg="send_to is None")
    
    send_by = input_params.get("send_by", None)
    if not send_by:
        exit_with_error(error_type=sdk.output_error_type.USER, 
                        error_code=err_code.USER_CONFIG_ERROR,
                        error_msg="send_by is None")
    send_by = json.loads(send_by)
    sdk.log.info("send_by is {}".format(send_by))

    title = input_params.get("title", None)
    if not title:
        exit_with_error(error_type=sdk.output_error_type.USER, 
                        error_code=err_code.USER_CONFIG_ERROR,
                        error_msg="title is None")

    content = input_params.get("content", None)
    if not content:
        exit_with_error(error_type=sdk.output_error_type.USER, 
                        error_code=err_code.USER_CONFIG_ERROR,
                        error_msg="content is None")

    bk_app_code = sdk.get_sensitive_conf("bk_app_code")
    bk_app_secret = sdk.get_sensitive_conf("bk_app_secret")
    bk_host = sdk.get_sensitive_conf("bk_host")
    bk_username = sdk.get_sensitive_conf("bk_username")
    if bk_app_code is None:
        exit_with_error(error_type=sdk.output_error_type.USER, error_code=err_code.USER_CONFIG_ERROR, error_msg="bk_app_code cannot be empty")
    
    if bk_app_secret is None:
        exit_with_error(error_type=sdk.output_error_type.USER, error_code=err_code.USER_CONFIG_ERROR, error_msg="bk_app_secret cannot be empty")
    
    if bk_host is None:
        exit_with_error(error_type=sdk.output_error_type.USER, error_code=err_code.USER_CONFIG_ERROR, error_msg="bk_host cannot be empty")
    bk_host = bk_host.rstrip("/")

    if bk_username is None:
        exit_with_error(error_type=sdk.output_error_type.USER, error_code=err_code.USER_CONFIG_ERROR, error_msg="bk_username cannot be empty")

    # 插件逻辑

    headers={"Content-Type": "application/json; charset=utf-8"}
    api_url = bk_host + "/api/c/compapi/cmsi/send_msg/"
    data_tpl = {
            "bk_app_code": bk_app_code,
            "bk_app_secret": bk_app_secret,
            "bk_username": bk_username,
            "msg_type": "weixin",
            "receiver__username": send_to,
            "title": title,
            "content": content,
            "body_format": "Text"
        }

    if "weixin" in send_by:
        data_tpl["msg_type"] = "weixin"
        data=json.dumps(data_tpl)
        sdk.log.info("【weixin】 send data is {}".format(data))
        resp = requests.post(
            url=api_url, 
            headers=headers, 
            data=data
        )
        if resp.status_code != 200:
            exit_with_error(error_type=sdk.output_error_type.THIRD_PARTY, 
                            error_code=err_code.THIRD_PARTY,
                            error_msg=resp.text)
        resp_json = resp.json()
        
        sdk.log.info("【weixin】 response data is {}".format(resp_json))
        if resp_json["code"] != 0:
            exit_with_error(error_type=sdk.output_error_type.USER, 
                            error_code=err_code.USER_CONFIG_ERROR,
                            error_msg=resp_json["message"])
            # sdk.log.error("{}".format(resp_json['message']))

    if "mail" in send_by:
        data_tpl["msg_type"] = "mail"
        data = json.dumps(data_tpl)
        sdk.log.info("【mail】 send data is {}".format(data))
        resp = requests.post(
            url=api_url, 
            headers=headers, 
            data=data
        )
        if resp.status_code != 200:
            exit_with_error(error_type=sdk.output_error_type.THIRD_PARTY, 
                            error_code=err_code.THIRD_PARTY,
                            error_msg=resp.text)
        resp_json = resp.json()
        sdk.log.info("【mail】 response data is {}".format(resp_json))
        if resp_json["code"] != 0:
            exit_with_error(error_type=sdk.output_error_type.USER, 
                            error_code=err_code.USER_CONFIG_ERROR,
                            error_msg=resp_json["message"])
            # sdk.log.error("{}".format(resp_json['message']))
    
    # 插件执行结果、输出数据

    exit_with_succ()

