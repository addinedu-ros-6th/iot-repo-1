#include <Servo.h>
#include <DHT11.h>

#define DHTTYPE DHT11  
#define DHTPIN 10
DHT11 dht11(10);

int ENA = A14;
int INA1 = 6;
int INA2 = 7;

Servo myServo;  // Servo 객체 생성
int servoPin = 8; 

int ENA1 = A7;
int waterIN1 = 22;
int waterIN2 = 24;
int relayPin = 9;

int ldrPin = A0;  
int ledPin_green = 3; 
int ledPin_hot = 2;

int soil_sensorPin = A1;

unsigned long previousMillis1 = 0;
unsigned long previousMillis2 = 0;
unsigned long previousMillis3 = 0;
unsigned long previousMillis4 = 0;
unsigned long previousMillis5 = 0;
unsigned long previousMillis6 = 0;
unsigned long previousMillis7 = 0;

unsigned long interval1 = 780;
unsigned long interval2 = 3000;
unsigned long interval3 = 400;
unsigned long interval4 = 500;
unsigned long interval5 = 3000;
unsigned long interval6 = 400;
unsigned long interval7 = 780;

bool processState1 = false;
bool processState2 = false;
bool processState3 = false;
bool processState4 = false;
bool processState5 = false;
bool processState6 = false;
bool processState7 = false;

unsigned long previousServoMillis = 0;
const int servoInterval = 20; // 각도 변경 간격 (20ms)
int servoAngle = 0;
bool servoIncreasing = true;
int servoStep = 1; // 각도 변경 단위
int servoCount = 0;
bool servoActive = false;

enum StatusCode : byte {
  STATUS_OK,
  STATUS_ERROR,
  STATUS_INVALID,
  STATUS_UNKNOWN_COMMAND = 0x03
};

void toBytes(byte* buffer, int data, int offset = 0) {
  buffer[offset] = data & 0xFF;
  buffer[offset + 1] = (data >> 8) & 0xFF;
}

void setup() {
  Serial.begin(9600);

  pinMode(ENA, OUTPUT);
  pinMode(INA1, OUTPUT);
  pinMode(INA2, OUTPUT);
  analogWrite(ENA, 0);
  digitalWrite(INA1, LOW);
  digitalWrite(INA2, LOW);

  myServo.write(0);
  myServo.attach(servoPin);

  pinMode(relayPin, OUTPUT);  // 릴레이 핀을 출력 모드로 설정
  digitalWrite(relayPin, LOW); // 펌프를 초기 상태에서 끈 상태로 유지

  pinMode(ledPin_green, OUTPUT);
  pinMode(ledPin_hot, OUTPUT);
}

void loop() {
  unsigned long currentMillis = millis();  // 현재 시간 얻기
  int recv_size = 0;
  char recv_buffer[16];

  if (Serial.available() > 0) {
    recv_size = Serial.readBytesUntil('\n', recv_buffer, 16);
  }

  if (recv_size > 0) 
  {
    char cmd[2];

    // 보낼 데이터 
    memset(cmd, 0x00, sizeof(cmd));
    memcpy(cmd, recv_buffer, 2);

    char send_buffer[16];
    memset(send_buffer, 0x00, sizeof(send_buffer));
    memcpy(send_buffer, cmd, 2);

    StatusCode status = StatusCode::STATUS_ERROR;

    // 환경 수치 요청
    if (strncmp(cmd, "GE", 2) == 0) 
    {
      memset(send_buffer + 2, StatusCode::STATUS_OK, 1);

      byte env[5];
      memset(env, 0x00, 5);
      status = readEnvValues(env);

      memset(send_buffer + 2, status, 1);
      memcpy(send_buffer + 3, env, 5);
      Serial.write(send_buffer, 8);
    }

    // 환경 제어 모듈 컨트롤(난방, 냉방, 워터)
    else if (strncmp(cmd, "SE", 2) == 0) 
    {
      status = toggleEnvControl((int)recv_buffer[2], true);

      memset(send_buffer + 2, status, 1);
      memset(send_buffer + 3, recv_buffer[2], 1);
      Serial.write(send_buffer, 4);
    }

    // 환경 제어 모듈 컨트롤(난방, 냉방, 워터)
    else if (strncmp(cmd, "EE", 2) == 0) {
      status = toggleEnvControl((int)recv_buffer[2], false);

      memset(send_buffer + 2, status, 1);
      memset(send_buffer + 3, recv_buffer[2], 1);
      Serial.write(send_buffer, 4);
    }

    // 애정 표현: 버튼을 눌렀을 때 서보 모터가 2번 왕복
    else if (strncmp(cmd, "SA", 2) == 0) {
      if ((int)recv_buffer[2] == 1 && !servoActive) 
      {
        servoActive = true; // 서보 모터 동작 활성화
        servoCount = 0;
        servoIncreasing = true;
        servoAngle = 0;
        myServo.write(servoAngle);
        previousServoMillis = millis(); // 현재 시간으로 초기화
      }

      status = STATUS_OK;
      memset(send_buffer + 2, status, 1);
      Serial.write(send_buffer, 3);
    }

    // 치료
    else if (strncmp(cmd, "ST", 2) == 0)
    {
      if ((int)recv_buffer[2] == 2)
      {
        // 워터펌프 실행
        if (processState4 && (currentMillis - previousMillis4 >= interval4)) {
          digitalWrite(relayPin, HIGH);  // 릴레이 활성화 (펌프 작동)
          previousMillis5 = currentMillis;
          processState4 = false;
          processState5 = true;
        }
        
      }

      //  위의 처리를 완료한 뒤에 아래의 코드를 실행 (status는 정상 작동인 경우에만 STATUS_OK)
      status = STATUS_OK;
      memset(send_buffer + 2, status, 1);
      memset(send_buffer + 3, recv_buffer[2], 1);
      Serial.write(send_buffer, 4);
    }
    else 
    {
      status = STATUS_UNKNOWN_COMMAND;
      memset(send_buffer + 2, status, 1);
      Serial.write(send_buffer, 3);
    }
    Serial.println();
  }

  // 서보 모터 동작 제어
  if (servoActive) {
    unsigned long currentMillis = millis();
    if (currentMillis - previousServoMillis >= servoInterval) {
      previousServoMillis = currentMillis;

      if (servoIncreasing) {
        servoAngle += servoStep;
        if (servoAngle >= 90) {
          servoAngle = 90;
          servoIncreasing = false;
        }
      } else {
        servoAngle -= servoStep;
        if (servoAngle <= 0) {
          servoAngle = 0;
          servoIncreasing = true;
          servoCount++;
        }
      }
      myServo.write(servoAngle);

      if (servoCount >= 2) {
        servoActive = false; // 서보 모터 동작 비활성화
        myServo.write(0); // 서보 모터를 0도로 위치
      }
    }
  }
}

StatusCode toggleEnvControl(int value, bool isOn) 
{
  switch (value) 
  {
    case 0:
      analogWrite(ENA, 255);
      digitalWrite(INA1, isOn);
      digitalWrite(INA2, HIGH); //////////////////////////쿨링팬
      break;
    case 1:
      digitalWrite(ledPin_hot, isOn);
      break;
    case 2:
      digitalWrite(relayPin, isOn);
      break;
    case 3:
      digitalWrite(ledPin_green, isOn);
      break;
    default:
      break;
  }

  return STATUS_OK;
}

StatusCode readEnvValues(byte* data) 
{
  int temp = random(2) == 0 ? 20 : 25; // 온도
  int humidity = analogRead(soil_sensorPin); //습도
  int light = analogRead(ldrPin); //조도


  byte buffer[5];
  memset(buffer, 0x00, sizeof(buffer));
  toBytes(data, temp, 0);
  toBytes(data, humidity, 2);
  toBytes(data, light, 4);

  return STATUS_OK;
}
