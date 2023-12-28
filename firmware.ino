#include <WiFi.h>
#include <ESPAsyncWebSrv.h>
#include <AccelStepper.h>

const char* ssid = "none";
const char* password = "12345678";

const int stepPinX = 32;
const int dirPinX = 26;
const int stepPinY = 33;
const int dirPinY = 27;
const int stepPinZ = 25;
const int dirPinZ = 14;
const int enablePin = 12;

AccelStepper stepperX(AccelStepper::DRIVER, stepPinX, dirPinX);
AccelStepper stepperY(AccelStepper::DRIVER, stepPinY, dirPinY);
AccelStepper stepperZ(AccelStepper::DRIVER, stepPinZ, dirPinZ);

// port 80
AsyncWebServer server(80);

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  pinMode(enablePin, OUTPUT);
  digitalWrite(enablePin, HIGH);

  stepperX.setMaxSpeed(500);
  stepperY.setMaxSpeed(500);
  stepperZ.setMaxSpeed(500);
  stepperX.setAcceleration(10000);
  stepperY.setAcceleration(10000);
  stepperZ.setAcceleration(10000);

  // Route for handling motor control
  server.on("/control", HTTP_GET, [](AsyncWebServerRequest *request){
    String stepsX, speedX, stepsY, speedY, stepsZ, speedZ;

    if (request->hasParam("stepsX") && request->hasParam("speedX") &&
        request->hasParam("stepsY") && request->hasParam("speedY") &&
        request->hasParam("stepsZ") && request->hasParam("speedZ")) {

      stepsX = request->getParam("stepsX")->value();
      speedX = request->getParam("speedX")->value();
      stepsY = request->getParam("stepsY")->value();
      speedY = request->getParam("speedY")->value();
      stepsZ = request->getParam("stepsZ")->value();
      speedZ = request->getParam("speedZ")->value();

      controlSteppers(stepsX.toInt(), speedX.toFloat(), stepsY.toInt(), speedY.toFloat(), stepsZ.toInt(), speedZ.toFloat());
      request->send(200, "text/plain", "Motors commanded successfully");
    } else {
      request->send(400, "text/plain", "Invalid parameters");
    }
  });

  server.begin();
}
  static bool motorsStopped = true;

void loop() {
  stepperX.run();
  stepperY.run();
  stepperZ.run();



   if (stepperX.distanceToGo() == 0 && stepperY.distanceToGo() == 0 && stepperZ.distanceToGo() == 0) {
    if (!motorsStopped) {
      delay(500);
      digitalWrite(enablePin, HIGH);
      Serial.println("Motors stopped");
      motorsStopped = true;
    }
  } else {
    motorsStopped = false;
  }


  // if (stepperX.distanceToGo() == 0 && stepperY.distanceToGo() == 0 && stepperZ.distanceToGo() == 0) {
  //   //maybe add a delay() ?
  //   //Serial.println("lol");
  //   //delay(100);
  //   digitalWrite(enablePin, HIGH);
  // }
}

void controlSteppers(int stepsX, float speedX, int stepsY, float speedY, int stepsZ, float speedZ) {
  digitalWrite(enablePin, LOW);

  stepperX.setMaxSpeed(speedX);
  stepperY.setMaxSpeed(speedY);
  stepperZ.setMaxSpeed(speedZ);

  stepperX.move(stepsX);
  stepperY.move(stepsY);
  stepperZ.move(stepsZ);
}
