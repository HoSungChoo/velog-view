import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QPushButton
from PyQt5.QtCore import Qt, QTimer
from GetTotalViewFromVelog import order
from enum import Enum

# Style 모음
class Style(Enum):
    board = "border: 1px solid black;"
    padding = "padding: 1px;"
    font = "font-family: 'Consolas'; font-size: 9pt;"

    pushButton_back = "background-color: #F1F0E8;"
    pushButton_color = "color: black;"

    text_back = "background-color: #F1F0E8;"

    label_back = "background-color: #E4E4D0;"

    back = "background-color: #EEE0C9;"


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # init value
        size = [[380, 20], [380, 200], [380, 20], [380, 30], [380, 20], [170, 30], [170, 30], [380, 20]]
        ypos = 10
        interval = 10

        self.widgets = [QLabel(self), QTextEdit(self), QLabel(self), QTextEdit(self), QLabel(self),
                        QPushButton("시작", self), QPushButton("나가기", self), QLabel(self)]

        # 위젯 정의
        self.widgets[0].setText("access token 입력")
        self.widgets[0].setStyleSheet(Style.padding.value + Style.font.value)

        self.widgets[1].setStyleSheet(
            Style.board.value + Style.padding.value + Style.font.value + Style.text_back.value)

        self.widgets[2].setText("velog 닉네임 입력")
        self.widgets[2].setStyleSheet(Style.padding.value + Style.font.value)

        self.widgets[3].setStyleSheet(
            Style.board.value + Style.padding.value + Style.font.value + Style.text_back.value)

        self.widgets[4].setStyleSheet(
            Style.board.value + Style.padding.value + Style.font.value + Style.label_back.value)

        self.widgets[5].setText("시작")
        self.widgets[5].clicked.connect(self.start)
        self.widgets[5].setStyleSheet(
            Style.board.value + Style.padding.value + Style.font.value + Style.pushButton_back.value + Style.pushButton_color.value)

        self.widgets[6].setText("나가기")
        self.widgets[6].clicked.connect(self.close)
        self.widgets[6].setStyleSheet(
            Style.board.value + Style.padding.value + Style.font.value + Style.pushButton_back.value + Style.pushButton_color.value)

        self.widgets[7].setText("오류 발생 시 hosung0610@google.com 으로 문의주세요.")
        self.widgets[7].setAlignment(Qt.AlignCenter)
        self.widgets[7].setStyleSheet(
            Style.board.value + Style.padding.value + Style.font.value + Style.label_back.value)

        # set size
        for i in range(len(size)):
            self.widgets[i].setGeometry(10, ypos, size[i][0], size[i][1])

            if i != 5:
                ypos = ypos + size[i][1] + interval

        self.widgets[5].setGeometry(10, 350, size[5][0], size[5][1])
        self.widgets[6].setGeometry(220, 350, size[6][0], size[6][1])

        # 전체 설정
        self.setWindowTitle('벨로그 총 조회수 측정기')
        self.setStyleSheet(Style.back.value)
        self.setFixedSize(400, ypos)
        self.show()

    # 시작 버튼과 연결된 함수
    def start(self):
        # access_token, username 추출
        access_token = self.widgets[1].toPlainText().strip()
        username = self.widgets[3].toPlainText().strip()

        if self.validateInput(access_token, username) is False:
            return

        # 함수 실행 전 준비
        self.widgets[4].setText("계산 중..")
        self.widgets[5].setEnabled(False)
        self.widgets[6].setEnabled(False)

        # 조회수 추출 함수 실행
        QTimer.singleShot(100, lambda: self.calculate(access_token=access_token, username=username))

        return

    # 조회수 반환 함수
    def calculate(self, access_token, username):
        result = order(access_token=access_token, username=username)

        # 예외처리
        self.widgets[4].setText(self.validateResult(result))

        # 함수 실행 후 처리
        self.widgets[5].setEnabled(True)
        self.widgets[6].setEnabled(True)

    # 결과에 대한 예외 처리 반환 함수
    def validateResult(self, result):
        if result['type'] == 'error' and result['status'] == 401:
            return result['detail']

        if result['type'] == 'error' and result['status'] == 204:
            return result['detail']

        if result['type'] == 'success':
            return f"공개 포스트 수 : {result['data']['number of posts']} / 전체 조회수 : {result['data']['total view']}"

    # 입력에 대한 예외 처리 반환 함수
    def validateInput(self, access_token, username):
        if not access_token:
            self.widgets[4].setText("access token을 입력해주세요.")
            return False

        elif not username:
            self.widgets[4].setText("닉네임을 입력해주세요.")
            return False

        return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
