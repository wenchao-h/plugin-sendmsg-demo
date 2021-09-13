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
    # 企业微信/邮件配置
    send_by = []
    send_to = ""
    title = ""
    content = ""
    send_by_str = input_params.get("send_by", None)
    if send_by_str:
        send_by = json.loads(send_by_str)
        sdk.log.info("send_by is {}".format(send_by))
        if len(send_by) > 0:

            send_to = input_params.get("send_to", None)
            if not send_to:
                exit_with_error(error_type=sdk.output_error_type.USER, 
                                error_code=err_code.USER_CONFIG_ERROR,
                                error_msg="send_to is None")
            sdk.log.info("send_to is {}".format(send_to))

            title = input_params.get("title", None)
            if not title:
                exit_with_error(error_type=sdk.output_error_type.USER, 
                                error_code=err_code.USER_CONFIG_ERROR,
                                error_msg="title is None")
            sdk.log.info("title is {}".format(title))

            content = input_params.get("content", None)
            if not content:
                exit_with_error(error_type=sdk.output_error_type.USER, 
                                error_code=err_code.USER_CONFIG_ERROR,
                                error_msg="content is None")
            sdk.log.info("content is {}".format(content))

    # 企业微信机器人配置
    send_by_robot_str = input_params.get("send_by_robot", None)
    sdk.log.info("send_by_robot is {}".format(send_by_robot_str))
    send_by_robot = False
    robot_key = ""
    msgtype = "text"
    mentioned_list = []
    robot_content = ""
    if send_by_robot_str == "true":
        send_by_robot = True

        robot_key = input_params.get("robot_key", None)
        if not robot_key:
            exit_with_error(error_type=sdk.output_error_type.USER, 
                            error_code=err_code.USER_CONFIG_ERROR,
                            error_msg="robot_key is None")
        sdk.log.info("robot_key is {}".format(robot_key))
        
        msgtype = input_params.get("msgtype", None)
        if not msgtype:
            exit_with_error(error_type=sdk.output_error_type.USER, 
                            error_code=err_code.USER_CONFIG_ERROR,
                            error_msg="msgtype is None")
        sdk.log.info("msgtype is {}".format(msgtype))
        
        if msgtype == "text":
            mentioned = input_params.get("mentioned", None)
            if mentioned:
                mentioned_list = mentioned.split(";")
            sdk.log.info("mentioned_list is {}".format(mentioned_list))

        robot_content = input_params.get("robot_content", None)
        if not robot_content:
            exit_with_error(error_type=sdk.output_error_type.USER, 
                            error_code=err_code.USER_CONFIG_ERROR,
                            error_msg="robot_content is None")
        sdk.log.info("robot_content is {}".format(robot_content))

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

    
    sdk.log.info("send_by is {}".format(send_by))
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
    
    if send_by_robot:
        robot_webhook = sdk.get_sensitive_conf("robot_webhook")
        if robot_webhook is None:
            exit_with_error(error_type=sdk.output_error_type.USER, 
                            error_code=err_code.USER_CONFIG_ERROR,
                            error_msg="robot_webhook does not set")
        body = {
            "msgtype": "text",
            "text": {
                "content": "",
                "mentioned_list":mentioned_list
            },
            "markdown": {
                "content": ""
            }
        }
        body["msgtype"] = msgtype
        body[msgtype]["content"] = robot_content
        sdk.log.info("【robot】 send data is is {}".format(body))
        webhook_url = robot_webhook + "?key=" + robot_key
        sdk.log.info("webhook_url is {}".format(webhook_url))
        
        resp = requests.post(url=webhook_url, headers=headers, data=json.dumps(body))
        if resp.status_code != 200:
            exit_with_error(error_type=sdk.output_error_type.THIRD_PARTY, 
                            error_code=err_code.THIRD_PARTY,
                            error_msg=resp.text)
        resp_json = resp.json()
        sdk.log.info("【robot】 response data is {}".format(resp_json))
    # 插件执行结果、输出数据
    if not send_by and not send_by_robot :
        sdk.log.error("用户没有选择任何的发送方式")
    data = {
        "TEST_OUTPUT":{
            "type": sdk.output_field_type.STRING,   # 需要task.json设置的类型一致
            "value": "test"                         # 输出变量的值，需和声明的类型一致
        }
    }
    exit_with_succ()

