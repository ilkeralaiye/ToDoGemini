    // Add Todo JS
    const todoForm = document.getElementById('todoForm');
    if (todoForm) {
        todoForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            const payload = {
                title: data.title,
                description: data.description,
                priority: parseInt(data.priority),
                complete: false
            };

            try {
                const response = await fetch('/todo/create_todo', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${getCookie('access_token')}`
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    form.reset(); // Clear the form
                } else {
                    // Handle error
                    const errorData = await response.json();
                    alert(`Error: ${errorData.detail}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            }
        });
    }

    // Edit Todo JS
    const editTodoForm = document.getElementById('editTodoForm');
    if (editTodoForm) {
        editTodoForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            var url = window.location.pathname;
            const todoId = url.substring(url.lastIndexOf('/') + 1);

            const payload = {
                title: data.title,
                description: data.description,
                priority: parseInt(data.priority),
                complete: data.complete === "on"
            };

            try {
                const token = getCookie('access_token');
                if (!token) {
                    throw new Error('Authentication token not found');
                }

                const response = await fetch(`/todo/update_todo/${todoId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    window.location.href = '/todo/todo-page'; // Redirect to the todo page
                } else {
                    // Handle error
                    const errorData = await response.json();
                    alert(`Error: ${errorData.detail}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            }
        });

        document.getElementById('deleteButton').addEventListener('click', async function () {
            var url = window.location.pathname;
            const todoId = url.substring(url.lastIndexOf('/') + 1);

            try {
                const token = getCookie('access_token');
                if (!token) {
                    throw new Error('Authentication token not found');
                }

                const response = await fetch(`/todo/delete_todo/${todoId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    // Handle success
                    window.location.href = '/todo/todo-page'; // Redirect to the todo page
                } else {
                    // Handle error
                    const errorData = await response.json();
                    alert(`Error: ${errorData.detail}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            }
        });
    }

    // Login JS
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const form = event.target;
            const formData = new FormData(form);

            const payload = new URLSearchParams();
            for (const [key, value] of formData.entries()) {
                payload.append(key, value);
            }

            try {
                const response = await fetch('/auth/token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: payload.toString()
                });

                if (response.ok) {
                    const data = await response.json();
                    logout();
                    document.cookie = `access_token=${data.access_token}; path=/`;
                    window.location.href = '/todo/todo-page'; // Redirect to todo page
                } else {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.detail}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            }
        });
    }

const registerForm = document.getElementById('registerForm');
console.log("registerForm:", registerForm); // Check if registerForm is found
if (registerForm) {
    registerForm.addEventListener('submit', async function (event) {
        console.log('Form submitted!'); // Check if the event is triggered
        event.preventDefault(); // Verify the position of this call

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        console.log("data:", data);

        let trimmedPassword = ""; // initialize the variable
        let trimmedVerifyPassword = ""; // initialize the variable

        if(data.password){ // check if data.password is defined
            trimmedPassword = data.password.trim();
        }

        if(data.verify_password){ // check if data.verify_password is defined
            trimmedVerifyPassword = data.verify_password.trim();
        }

        console.log("trimmedPassword:", trimmedPassword);
        console.log("trimmedVerifyPassword:", trimmedVerifyPassword);

        if (trimmedPassword !== trimmedVerifyPassword) {
            alert("Passwords do not match");
            return;
        }

        const payload = {
            email: data.email,
            userName: data.username, // Corrected: userName
            firstName: data.firstname, // Corrected: firstName
            lastName: data.lastname, // Corrected: lastName
            phoneNumber: data.phone_number, // Corrected: phoneNumber
            password: data.password,
        };
        console.log("Payload:", payload); // Check the payload content

        try {
            console.log("Before fetch"); // Check if it reach the fetch part
            const response = await fetch('/auth/create_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            console.log("After fetch", response); // Check the response

            if (response.ok) {
                window.location.href = '/auth/login-page';
            } else {
                const errorData = await response.json();
                let errorMessage = "Registration failed:\n";
                for (const key in errorData) {
                    errorMessage += `${key}: ${errorData[key]}\n`;
                }
                alert(errorMessage);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
}

    // Helper function to get a cookie by name
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    function logout() {
        // Get all cookies
        const cookies = document.cookie.split(";");

        // Iterate through all cookies and delete each one
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i];
            const eqPos = cookie.indexOf("=");
            const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
            document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
        }

        window.location.href = '/auth/login-page';
    };
