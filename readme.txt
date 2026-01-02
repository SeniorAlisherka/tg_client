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
