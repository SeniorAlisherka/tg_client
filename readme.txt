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

Как добавлять менюшки и event handlers: 
Менюшки называешь menu_{name}, функция самой менюшки - on_menu_{name}.
Функция каждого выбора - on_menu_{name}_{choice}
Новый event handler ты называешь по @type прилетающему, т.е. on_{type}.
Функцию для определенного extra надо назвать on_{type}_{extra}.
Для определенных функций типа on_error, on_updateAuthorizationState, где 
нужно для каждого message или state нужна отдельная функция 
создаешь свой dispatcher внутри функции,
у меня для обеих этих функций диспатчер ищет 
on_error_{code}, если не нашел то on_error_{message},
on_state_{state} функции соответственно,
советую так и продолжать

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