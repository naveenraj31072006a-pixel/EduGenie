document
    .querySelectorAll(".ai-action")
    .forEach(function(button) {


        button.addEventListener(
            "click",
            async function() {


                const promptElement =
                    document.getElementById(
                        "prompt"
                    );


                const result =
                    document.getElementById(
                        "aiResult"
                    );


                const badge =
                    document.getElementById(
                        "providerBadge"
                    );


                const prompt =
                    promptElement.value.trim();


                if (!prompt) {

                    result.innerHTML =
                        "<p>Please enter a topic or question first.</p>";

                    return;

                }


                result.innerHTML =
                    "<p>EduGenie is thinking...</p>";


                badge.textContent =
                    "Generating...";


                try {


                    const response =
                        await fetch(
                            "/api/ai",
                            {

                                method: "POST",

                                headers: {

                                    "Content-Type":
                                        "application/json"

                                },

                                body: JSON.stringify({

                                    prompt: prompt,

                                    mode:
                                        button.dataset.mode

                                })

                            }
                        );


                    const data =
                        await response.json();


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            "Request failed"
                        );

                    }


                    result.textContent =
                        data.answer;


                    if (
                        data.provider
                        === "gemini"
                    ) {

                        badge.textContent =
                            "Gemini AI";

                    } else {

                        badge.textContent =
                            "Demo Mode";

                    }


                } catch (error) {


                    result.innerHTML =
                        `<p>
                            Something went wrong:
                            ${error.message}
                        </p>`;


                    badge.textContent =
                        "Error";

                }

            }

        );

    });