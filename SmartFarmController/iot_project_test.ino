enum StatusCode : byte{
  STATUS_OK,
  STATUS_ERROR,
  STATUS_INVALID,
  STATUS_UNKNOWN_COMMAND = 0x03
};

void toBytes(byte* buffer, int data, int offset = 0)
{
  buffer[offset] = data & 0xFF;
  buffer[offset + 1] = (data >> 8) & 0xFF;
}


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  int recv_size = 0;
  char recv_buffer[16];

  if (Serial.available() > 0)
  {
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
      // 메모리 맨 앞 2자리는 cmd
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
    else if (strncmp(cmd, "EE", 2) == 0)
    {
      status = toggleEnvControl((int)recv_buffer[2], false);

      memset(send_buffer + 2, status, 1);
      memset(send_buffer + 3, recv_buffer[2], 1);
      Serial.write(send_buffer, 4);
    }

    // 애정 표현
    else if (strncmp(cmd, "SA", 2) == 0)
    {
      if ((int)recv_buffer[2] == 1)
      {
        // 초음파 실행시켜주세요. 
        status = STATUS_OK;
        memset(send_buffer + 2, status, 1);
        Serial.write(send_buffer, 3);
      }
    }

    // 치료
    else if (strncmp(cmd, "ST", 2) == 0)
    {
      if ((int)recv_buffer[2] == 0)
      {
        // 치료제(감염)을 실행
      }
      else if ((int)recv_buffer[2] == 1)
      {
        // 가습기(해충)을 실행
      }
      else if ((int)recv_buffer[2] == 2)
      {
        // 영양제(노란잎)을 실행
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
  } // if
} // loop


StatusCode toggleEnvControl(int value, bool isOn)
{
  // 여기서 digitalWrite High 
  switch (value)
  {
    case 0:
      // 에어컨
      // digitalWrite(, isOn)
      break;
    case 1:
      // 난방 
      break;
    case 2: 
      // 워터
      break;
    case 3:
      // 생장 LED
      break;
    default:
      break;
  }

  return STATUS_OK;
}

StatusCode readEnvValues(byte* data)
{
  // 여기에 digitalread 값 넣으셔요.
  int aircon = 20;
  int heating = 2;
  int light = 20;

  byte buffer[5];
  memset(buffer, 0x00, sizeof(buffer));
  toBytes(data, aircon, 0);   // 0-1 바이트
  toBytes(data, heating, 2);  // 2-3 바이트
  toBytes(data, light, 4);    // 4-5 바이트

  return STATUS_OK;
}



