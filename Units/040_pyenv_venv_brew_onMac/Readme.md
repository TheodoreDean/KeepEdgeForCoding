### Version control and switch on Mac ###
#### Steps #####


> 1. 
```

brew update
brew install pyenv

```

> 2 configure

```
#zsh
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

                        
```
```
#bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init --path)"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
source ~/.bash_profile

```

> 3. install and switch

```
pyenv install 3.x.x  # 替换3.x.x为你想安装的Python版本号，例如3.8.5

pyenv global 3.x.x  # 替换3.x.x为你想使用的Python版本号


# 安装 pyenv 和 Python 3.12
brew install pyenv
pyenv install 3.12.0

# 创建并激活虚拟环境
pyenv local 3.12.0
python -m venv my_project
source my_project/bin/activate
```
> 4. refer to[!https://blog.csdn.net/ZHY0091/article/details/147730167]
[!https://blog.csdn.net/ttumetai/article/details/147455207]


