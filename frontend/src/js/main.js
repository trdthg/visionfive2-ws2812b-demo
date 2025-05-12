import { logSomething } from "./module";
import { logSomethingBig } from "./module";

import * as bootstrap from "bootstrap";
import "@fortawesome/fontawesome-free/js/fontawesome";
import "@fortawesome/fontawesome-free/js/solid";
import "@fortawesome/fontawesome-free/js/regular";
import "@fortawesome/fontawesome-free/js/brands";

/* Easter egg */
logSomethingBig("Nyahallo~Stop!");
logSomething(
    "This is a browser feature intended for developers. If someone told you to copy and paste something here to enable a feature or \"hack\", it is a scam."
);
logSomething(
    "See https://en.wikipedia.org/wiki/Self-XSS for more information."
);

const baseUrl = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", async () => {

    /* first, check light status */
    const span = document.querySelector(".badge");
    const lightswitch = document.querySelector("#lightswitch");

    try {
        const response = await fetch(`${baseUrl}/lightstatus`);
        const data = await response.json();

        if (response.status === 200 && data.status === true) {
            // 请求成功，将 class 内的 bg-secondary 改变成 bg-success，并且 Unknown 改变成 On
            span.classList.remove("bg-secondary");
            span.classList.add("bg-success");
            span.textContent = "On";

            // 将 lightswitch 的 checked 属性设置为 true，以将其标记为已选中
            lightswitch.checked = true;
        } else if (response.status === 200 && data.status === false) {
            // 请求成功，将 class 内的 bg-secondary 改变成 bg-danger，并且 Unknown 改变成 Off
            span.classList.remove("bg-secondary");
            span.classList.add("bg-danger");
            span.textContent = "Off";

            // 将 lightswitch 的 checked 属性设置为 false，以将其标记为未选中
            lightswitch.checked = false;
        } else {
            // 请求失败，该元素保持不变
            console.log("Failed to get light status.");
        }
    } catch (error) {
        console.log(error);
    }

    /* 更新灯的状态 */
    function updateLightStatus(status) {
        const span = document.querySelector(".badge");
    
        if (status) {
            span.classList.remove("bg-danger");
            span.classList.add("bg-success");
            span.textContent = "On";
        } else {
            span.classList.remove("bg-success");
            span.classList.add("bg-danger");
            span.textContent = "Off";
        }
    }

    /* send to backend */
    const label = document.querySelector("input[id=\"lightswitch\"]");
    const input = document.querySelector("#lightswitch");

    label.addEventListener("click", async () => {
        if (!input.checked) {
            // 关闭灯光
            const response = await fetch(`${baseUrl}/setlight?switch=off`, {
                method: "POST",
            });
            const data = await response.json();
        
            if (response.status === 200 && data.result === "success" && data.status === "off") {
                // 请求成功，弹出成功的 toast
                showToast("Light is off!");
                updateLightStatus(false);
            } else if (response.status === 400 && data.result === "failed" && data.status === "off") {
                // 请求成功，但是状态为 off，弹出失败的 toast，并且撤销 label 的更改状态
                input.checked = !input.checked;
                label.querySelector("input").checked = true;
                showToast("Light is already off!");
            } else if (response.status === 400 && data.result === "error" && data.message === "Invalid parameter") {
                // 请求失败，弹出失败的 toast，并且撤销 label 的更改状态
                input.checked = !input.checked;
                label.querySelector("input").checked = true;
                showToast("Invalid parameter!");
            } else {
                // 请求失败，弹出失败的 toast，并且撤销 label 的更改状态
                input.checked = !input.checked;
                label.querySelector("input").checked = true;
                showToast("Failed to turn off the light!");
            }
        } else {
            // 打开灯光
            const response = await fetch(`${baseUrl}/setlight?switch=on`, {
                method: "POST",
            });
            const data = await response.json();
        
            if (response.status === 200 && data.result === "success" && data.status === "on") {
                // 请求成功，弹出成功的 toast
                showToast("Light is on!");
                updateLightStatus(true);
            } else if (response.status === 400 && data.result === "failed" && data.status === "on") {
                // 请求成功，但是状态为 on，弹出失败的 toast，并且撤销 label 的更改状态
                input.checked = !input.checked;
                label.querySelector("input").checked = false;
                showToast("Light is already on!");
            } else if (response.status === 400 && data.result === "error" && data.message === "Invalid parameter") {
                // 请求失败，弹出失败的 toast，并且撤销 label 的更改状态
                input.checked = !input.checked;
                label.querySelector("input").checked = false;
                showToast("Invalid parameter!");
            } else {
                // 请求失败，弹出失败的 toast，并且撤销 label 的更改状态
                input.checked = !input.checked;
                label.querySelector("input").checked = false;
                showToast("Failed to turn on the light!");
            }
        }
    });

    /* change color */
    const lightColorInput = document.querySelector("#lightcolor");
    const sendColorButton = document.querySelector("#sendcolor");
    
    sendColorButton.addEventListener("click", async () => {
        const colorValue = lightColorInput.value.replace("#", "");
        const url = `${baseUrl}/setcolor?value=${colorValue}`;
        
        try {
            const response = await fetch(url, {
            method: "POST"
            });
        
            if (response.status === 200) {
            const data = await response.json();
            showToast(`Color set to (${data.color})`);
            } else {
            const data = await response.json();
            showToast(data.message);
            }
        } catch (error) {
            console.error(error);
            showToast("An error occurred while setting color");
        }
    });

    /* change brightness */
    const lightBrightnessInput = document.querySelector("#lightbrightness");

    lightBrightnessInput.addEventListener("change", async () => {
        const brightnessValue = lightBrightnessInput.value;
        const url = `${baseUrl}/setbrightness?value=${brightnessValue}`;
        
        try {
                const response = await fetch(url, {
                method: "POST"
            });
        
            if (response.status === 200) {
                const data = await response.json();
                showToast(`Brightness set to ${data.brightness}`);
            } else {
                const data = await response.json();
                showToast(data.message);
            }
        } catch (error) {
            console.error(error);
            showToast("An error occurred while setting brightness");
        }
    });

    /* Toast */
    function showToast(message) {
            //console.log("show toast", message);
            const toast = new bootstrap.Toast(document.querySelector(".toast"));

            // 设置 toast 的标题和内容
            const toastBody = document.querySelector(".toast-body");
            toastBody.textContent = message;

            // 显示 toast
            toast.show();
        }
});

