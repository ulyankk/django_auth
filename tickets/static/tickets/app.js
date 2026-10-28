const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            ...(options.headers || {})
        },
        credentials: "same-origin"
    });

    let data = null;
    if (response.status !== 204) {
        data = await response.json().catch(() => null);
    }
    if (!response.ok) {
        throw new Error(JSON.stringify(data || { detail: "Ошибка выполнения запроса" }));
    }
    return data;
}

const categorySelect = document.getElementById("category");
const form = document.getElementById("ticket-form");
const titleInput = document.getElementById("title");
const message = document.getElementById("message");
const list = document.getElementById("tickets-list");
const loading = document.getElementById("loading");
const filter = document.getElementById("status-filter");

function showMessage(text, isError = false) {
    message.textContent = text;
    message.className = "alert " + (isError ? "alert-danger" : "alert-success");
}

async function loadCategories() {
    const categories = await apiRequest("/api/categories/");
    categorySelect.replaceChildren();
    for (const category of categories) {
        const option = document.createElement("option");
        option.value = category.id;
        option.textContent = category.name;
        categorySelect.append(option);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
        await apiRequest("/api/tickets/", {
            method: "POST",
            body: JSON.stringify({
                title: titleInput.value,
                category: Number(categorySelect.value)
            })
        });
        titleInput.value = "";
        showMessage("Заявка успешно создана");
        await loadTickets();
    } catch (error) {
        showMessage("Не удалось создать заявку: " + error.message, true);
    }
});

async function loadTickets() {
    loading.hidden = false;
    const params = new URLSearchParams();
    if (filter.value) {
        params.set("status", filter.value);
    }
    const query = params.toString();
    const url = "/api/tickets/" + (query ? "?" + query : "");

    try {
        const tickets = await apiRequest(url);
        list.replaceChildren();

        if (tickets.length === 0) {
            const empty = document.createElement("p");
            empty.textContent = "Заявки не найдены";
            list.append(empty);
            return;
        }

        for (const ticket of tickets) {
            const row = document.createElement("div");
            row.className = "d-flex justify-content-between align-items-center border-bottom py-3 gap-3";

            const title = document.createElement("div");
            title.textContent = ticket.title + " — " + ticket.category_name;

            const controls = document.createElement("div");
            controls.className = "d-flex align-items-center gap-2";

            const statusSelect = document.createElement("select");
            statusSelect.className = "form-select form-select-sm";
            statusSelect.style.width = "auto";

            if (ticket.status === "new") {
                statusSelect.innerHTML = `
                    <option value="new" selected>Новая</option>
                    <option value="progress">В работе</option>
                `;
            } else if (ticket.status === "progress") {
                statusSelect.innerHTML = `
                    <option value="progress" selected>В работе</option>
                    <option value="done">Выполнена</option>
                `;
            } else {
                statusSelect.innerHTML = `<option value="done" selected>Выполнена</option>`;
                statusSelect.disabled = true;
            }

            statusSelect.addEventListener("change", (e) => {
                changeStatus(ticket.id, e.target.value);
            });
            controls.append(statusSelect);

            const btnDelete = document.createElement("button");
            btnDelete.className = "btn btn-sm btn-outline-danger";
            btnDelete.textContent = "Удалить";
            btnDelete.onclick = () => deleteTicket(ticket.id, ticket.title);
            controls.append(btnDelete);

            row.append(title, controls);
            list.append(row);
        }
    } catch (error) {
        showMessage("Не удалось загрузить заявки: " + error.message, true);
    } finally {
        loading.hidden = true;
    }
}

filter.addEventListener("change", loadTickets);

async function changeStatus(ticketId, newStatus) {
    try {
        await apiRequest(`/api/tickets/${ticketId}/`, {
            method: "PATCH",
            body: JSON.stringify({ status: newStatus })
        });
        showMessage("Статус заявки успешно изменен"); 
        await loadTickets(); 
    } catch (error) {
        showMessage("Ошибка смены статуса: " + error.message, true);
        await loadTickets(); 
    }
}

async function deleteTicket(ticketId, ticketTitle) {
    const confirmed = confirm(`Вы уверены, что хотите удалить заявку «${ticketTitle}»?`);
    if (!confirmed) return;

    try {
        await apiRequest(`/api/tickets/${ticketId}/`, {
            method: "DELETE"
        });
        showMessage("Заявка успешно удалена");
        await loadTickets();
    } catch (error) {
        showMessage("Ошибка удаления: " + error.message, true);
    }
}

async function initialize() {
    try {
        await loadCategories();
        await loadTickets();
    } catch (error) {
        showMessage("Ошибка инициализации: " + error.message, true);
    }
}

initialize();