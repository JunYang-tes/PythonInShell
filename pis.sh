#!/bin/sh
#PythonIsShell

pis_init(){
    pis_server_addr='/tmp/PythonIsShell'data +%s
    pis_server $pis_server_addr
}
pis(){
    #send code to interface
    local codes=''
    while read line
    do
        codes=$codes'\n'$line
    done
    echo $codes | interface $pis_server_addr
    #run
    echo 'cmd exec' | interface -a $pis_server_addr --type ctrl
    #input & output
    interface --type io
}
pis_destroy(){
    echo 'cmd quit' | interface -a $pis_server_addr --type ctrl
    rm $pis_server_addr
    rm $pis_server_addr'_control'
    rm $pis_server_addr'_io'
}

pis <<~python
def func():{
    print 'this is a python func'
    if True:{
        print 'hoo'
    }else:{
        print 'foo'
    }
}
func()
~python
