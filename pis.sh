#!/bin/sh
#PythonIsShell

pis_init(){
    pis_server_addr='/tmp/PythonIsShell' data +%s
}
pis(){
    local codes=''
    while read line
    do
        codes=$codes'\n'$line
    done
    codes=$codes'\n''cmd exec'
    echo $codes | interface $pis_server_addr
}
pis_destroy(){
    echo 'cmd quit' | interface $pis_server_addr
    rm pis_server_addr
}
#this function is writed for debug
interface(){
    echo $1
    while read line
    do
        echo $line
    done
}
pis 0<<~python
def func():{
    print 'this is a python func'
    if true:{
        print 'hoo'
    }else{
        print 'foo'
    }
}
func()
~python
