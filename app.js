let token = "";
let uploadedFile = "";

const API = "http://127.0.0.1:8000";

async function login() {
    const res = await fetch(`${API}/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            username: document.getElementById("username").value,
            password: document.getElementById("password").value
        })
    });

    const data = await res.json();
    token = data.access_token;
    alert("Login successful!");
}

async function upload() {
    const file = document.getElementById("fileInput").files[0];

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API}/upload`, {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    uploadedFile = data.filename;

    const select = document.createElement("select");
    select.id = "target";

    data.columns.forEach(col => {
        const option = document.createElement("option");
        option.value = col;
        option.text = col;
        select.appendChild(option);
    });

    document.getElementById("columns").innerHTML = "";
    document.getElementById("columns").appendChild(select);
}

async function train() {
    const target = document.getElementById("target").value;

    const res = await fetch(`${API}/train`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({filename: uploadedFile, target: target})
    });

    const data = await res.json();
    alert("Training started: " + data.task_id);
}

async function loadDashboard() {
    const res = await fetch(`${API}/dashboard`, {
        headers: {"Authorization": "Bearer " + token}
    });

    const data = await res.json();
    const list = document.getElementById("history");
    list.innerHTML = "";

    data.forEach(item => {
        const li = document.createElement("li");
        li.innerText = item.task_id;
        list.appendChild(li);
    });
}