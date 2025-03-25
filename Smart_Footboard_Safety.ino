#define fsrPin A0  // Connect FSR sensor to Analog pin A0

void setup() {
    Serial.begin(9600);
    pinMode(fsrPin, INPUT);
}

int getAverageFSRReading() {
    int sum = 0;
    for (int i = 0; i < 10; i++) {  // Take 10 readings for noise reduction
        sum += analogRead(fsrPin);
        delay(5);
    }
    return sum / 10;
}

void loop() {
    int fsrValue = getAverageFSRReading();
    Serial.print("FSR Value: ");
    Serial.println(fsrValue);  // Print raw values for debugging

    if (fsrValue > 500) {  // Adjust threshold based on observed values
        Serial.println("PRESENT");
    } else {
        Serial.println("ABSENT");
    }
    delay(500);  // Reduce excessive serial output
}