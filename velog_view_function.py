import requests


def initReturnData(type, status, detail, data):
    return {'type': type, 'status': status, 'detail': detail, 'data': data}


# username을 기반으로 post 목록 추출
def getPostList(username, limit, cursor):
    # API 전송을 위한 초기 변수 생성
    url = 'https://v2cdn.velog.io/graphql'
    headers = {
        'Content-Type': 'application/json',
    }

    body = {
        'operationName': 'Posts',
        'variables': {
            'username': f'{username}',
            'limit': limit,
            'cursor': f'{cursor}'
        },
        'query': 'query Posts($cursor: ID, $username: String, $temp_only: Boolean, $tag: String, $limit: Int) { posts(cursor: $cursor, username: $username, temp_only: $temp_only, tag: $tag, limit: $limit) {id title}}'
    }

    # query 진행 및 결과 반환
    response = requests.post(url, json=body, headers=headers)

    # 결과 반환
    try:
        return initReturnData(type='success', status=200, detail='', data=response.json()['data']['posts'])

    # 오류 발생시 오류 정보를 반환
    except:
        return initReturnData(type='error', status=response.status_code, detail='', data='')


# post로부터 total view를 추출하는 함수
def getViewFromPosts(access_token, post_list):
    # post의 길이가 0인 경우 0을 반환
    if len(post_list) == 0:
        return 0

    # postId 추출 및 리스트에 저장
    post_id_list = [item['id'] for item in post_list]
    total = 0

    # postId, access_token을 기반으로 조회수를 추출 및 저장
    for post_id in post_id_list:
        total += getViewFromPostId(post_id, access_token)

    return initReturnData(type='success', status=200, detail='', data={'total': total})


# access token이 올바른지 검증하는 함수
def validateAccessToken(access_token):
    # 해당 API는 access token 유효성 오류보다 postId 유효성 오류를 선행해서 검증한다.
    # postId 유효성이 타당하고 access token이 해당 post 저자의 토큰과 다를 경우 'This post is not yours' 에러 메세지를 발생한다.
    # 따라서 기존에 존재하는 임의의 postId를 입력한 뒤 access token 유효성을 검증하는 방식을 이용했다.
    url = 'https://v2cdn.velog.io/graphql'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'access_token={access_token}'
    }

    body = {
        'operationName': 'GetStats',
        'variables': {
            'post_id': '748b6194-5604-478a-87e5-c98272a87574'
        },
        'query': 'query GetStats($post_id: ID!) {getStats(post_id: $post_id) {total}}'
    }
    response = requests.post(url, json=body, headers=headers)

    # access token이 유효하지 않을 경우 false를 반환
    if response.json()['data']['getStats'] is None and response.json()['errors'][0][
        'message'] == 'This post is not yours':
        return False

    return True


# postId와 access token을 기반으로 특정 post의 조회수를 추출하는 함수
def getViewFromPostId(post_id, access_token):
    url = 'https://v2cdn.velog.io/graphql'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'access_token={access_token}'
    }

    body = {
        'operationName': 'GetStats',
        'variables': {
            'post_id': f'{post_id}'
        },
        'query': 'query GetStats($post_id: ID!) {getStats(post_id: $post_id) {total}}'
    }
    response = requests.post(url, json=body, headers=headers)

    return response.json()['data']['getStats']['total']


# 전체 관리 함수
def order(access_token, username):
    cursor = ''
    size = 0
    result = 0

    # access token 확인
    if not validateAccessToken(access_token):
        return initReturnData(type='error', status=401, detail='access token이 올바른지 확인해주세요.', data={'total': 0})

    # post를 순회하며 전체 조회수와 포스트 수 추출
    while True:
        post_list = getPostList(username, 100, cursor)

        # post를 읽는 URL 주소가 잘못된 경우
        if post_list['type'] == 'error' and post_list['status'] == 404:
            return initReturnData(type='error', status=404, detail='404 오류 발생. 관리자에게 문의해주세요.',
                                  data={'number of posts': 0, 'total view': 0})

        # 더 읽을 post가 없는 경우
        if len(post_list['data']) == 0:
            break

        # postId와 access token을 기반으로 포스트 조회수 추출 및 저장
        result += getViewFromPosts(access_token=access_token, post_list=post_list['data'])['data']['total']
        size += len(post_list['data'])
        cursor = post_list['data'][-1]['id']  # 성능 문제로 다음 포스트를 읽기 위해 마지막 postId 저장

    # post가 없는 경우 예외 처리
    if size == 0:
        return initReturnData(type='error', status=204, detail='닉네임이 올바른지 혹은 포스트가 존재하는지 확인하세요.', data='')

    # 결과 반환
    return {'type': 'success', 'detail': '', 'data': {'number of posts': size, 'total view': result}}