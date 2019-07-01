// Auto generated code by esphome
// ========== AUTO GENERATED INCLUDE BLOCK BEGIN ===========
#include "esphome.h"
using namespace esphome;
// ========== AUTO GENERATED INCLUDE BLOCK END ==========="

void setup() {
  // ===== DO NOT EDIT ANYTHING BELOW THIS LINE =====
  // ========== AUTO GENERATED CODE BEGIN ===========
  App.set_name("esp_family");
  App.set_compilation_datetime(__DATE__ ", " __TIME__);
  LogComponent *logcomponent = App.init_log(115200, 512, UART_SELECTION_UART0);
  WiFiComponent *wificomponent = App.init_wifi();
  wificomponent->set_use_address("esp_family.local");
  WiFiAP wifiap = WiFiAP();
  wifiap.set_ssid("Ezequiel2");
  wifiap.set_password("2putipus");
  wificomponent->add_sta(wifiap);
  OTAComponent *otacomponent = App.init_ota();
  otacomponent->set_auth_password("2putipus");
  otacomponent->start_safe_mode();
  api::APIServer *api_apiserver = App.init_api_server();
  api_apiserver->set_password("2putipus");
  // =========== AUTO GENERATED CODE END ============
  // ========= YOU CAN EDIT AFTER THIS LINE =========
  App.setup();
}

void loop() {
  App.loop();
}
