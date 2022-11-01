"use strict";

class Controller {

    constructor() {

        document.getElementById("button-fwd").onclick = this.forwards.bind(this);
        document.getElementById("button-tle").onclick = this.turnLeft.bind(this);
        document.getElementById("button-sto").onclick = this.stop.bind(this);
        document.getElementById("button-tri").onclick = this.turnRight.bind(this);
        document.getElementById("button-bak").onclick = this.backwards.bind(this);
        
        document.getElementById("button-exp1").onclick = this.expression1.bind(this);
        document.getElementById("button-exp2").onclick = this.expression2.bind(this);
        document.getElementById("button-exp3").onclick = this.expression3.bind(this);
    }

    setJsonrpcUrl(url) {
        this.url = url;
        
        return this;
    }

    post(command, params, callback){

        if(this.url) {

            var xhr = new XMLHttpRequest();
            xhr.open("POST", this.url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.withCredentials = false;
            if(callback){
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 4 && xhr.status === 200) {
                        var json = JSON.parse(xhr.responseText);
                        callback(json);
                    }
                };
            }
            var data = JSON.stringify({"method": command, "params": params || [], "id":0, "jsonrpc": "2.0"});
            xhr.send(data);
        } else {
            console.error("The JSON-RPC URL is not set yet!");
        }
    }

    forwards(){
    
        this.post("forwards");
    }

    turnLeft(){
    
        this.post("turnLeft");
    }

    stop(){
    
        this.post("stop");
    }
    
    turnRight(){
    
        this.post("turnRight");
    }
    
    backwards(){
    
        this.post("backwards");
    }
    
    expression1(){
        this.post("displayExpression", ["1"]);
    }

    expression2(){
        this.post("displayExpression", ["2"]);
    }

    expression3(){
        this.post("displayExpression", ["3"]);
    }
};

window.onload = function(){

    let controller = new Controller().setJsonrpcUrl("http://localhost:4000/jsonrpc");
};
