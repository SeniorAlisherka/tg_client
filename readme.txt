что было сделано:
1) запустить в терминале, чтобы скачать 
xcode cmd line tools
brew
gh td
затем он компилирует libtdjson.dylib через cmakelists.txt

xcode-select --install
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install gperf cmake openssl
git clone https://github.com/tdlib/td.git
cd td
rm -rf build
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release -DOPENSSL_ROOT_DIR=/opt/homebrew/opt/openssl/ -DCMAKE_INSTALL_PREFIX:PATH=../tdlib ..
cmake --build . --target install
cd ..
cd ..
ls -l td/tdlib

2) полученные 2 файла (1 основной другой alias) я засунул в main_logic
3) написал свой tg_client.py

Как добавлять любые классы: 
менюшки называешь типа main
для каждой менюшки создаешь button_factory типа main
кнопки называешь типа main_1
действие кнопки называешь типа main_1
event_handlers называешь типа updateAuthorizationState
extra_handlers называешь типа updateAuthorizationState_main_1
helper называешь типа helper_{whatitdoes} типа helper_auth_wait_params


баги нерешаемые
1) пока вводишь пароль если нажимаешь ctrl c, то close отправляется, 
но ответ не приходит, потому что твой же инпут блокирует tdlib_loop.
делать его мейн тредом тупо (+ даже тогда при ctrl c он прекратит сам луп)
(+ даже если снова начать луп чтобы дождаться close, может прилететь снова
updateAuthorizationState wait for pswd и снова залочить) 
(+ это тупо очень)
выводить инпут в другой тред тоже тупо потому что ты нарушаешь правило,
update - handler - update - handler - update ...
Поэтому только так

при сборке: 
1) чекнуть работу logs (db)
2) в .env есть полный путь
3) терминал пишет clear