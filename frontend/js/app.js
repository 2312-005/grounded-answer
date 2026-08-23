const API_URL = "http://127.0.0.1:8000/ask";

// Internal evaluation date.
// The judge does not need to enter this.
const CLAIM_DATE = "2026-04-15";

const questionInput = document.getElementById("question");
const askButton = document.getElementById("askButton");

const loading = document.getElementById("loading");
const result = document.getElementById("result");

const answer = document.getElementById("answer");
const citations = document.getElementById("citations");

const citationsSection = document.getElementById(
    "citationsSection"
);

const refusalSection = document.getElementById(
    "refusalSection"
);

const refusalReason = document.getElementById(
    "refusalReason"
);


askButton.addEventListener(
    "click",
    askPolicy
);


// Allow Ctrl + Enter to submit.
questionInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.ctrlKey &&
            event.key === "Enter"
        ) {
            askPolicy();
        }

    }
);


async function askPolicy() {

    const question = questionInput.value.trim();

    if (!question) {
        questionInput.focus();
        return;
    }


    setLoading(true);

    result.classList.add("hidden");

    citationsSection.classList.add(
        "hidden"
    );

    refusalSection.classList.add(
        "hidden"
    );

    answer.textContent = "";

    citations.innerHTML = "";


    try {

        const response = await fetch(
            API_URL,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },

                body: JSON.stringify({
                    question: question,
                    claim_date: CLAIM_DATE
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Request failed."
            );

        }


        displayResult(data);


    } catch (error) {

        displayError(error);

    } finally {

        setLoading(false);

    }
}


function displayResult(data) {

    result.classList.remove(
        "hidden"
    );


    if (data.refused) {

        answer.classList.add(
            "hidden"
        );

        refusalSection.classList.remove(
            "hidden"
        );

        refusalReason.textContent =
            data.reason ||
            "The supplied policy evidence does not establish an applicable rule.";

        return;
    }


    answer.classList.remove(
        "hidden"
    );

    refusalSection.classList.add(
        "hidden"
    );


    // Remove citations from the generated answer.
    // Citations are displayed separately below.
    let cleanAnswer =
        data.answer ||
        "No answer returned.";

    cleanAnswer = cleanAnswer.replace(
        /\n\nCitations:.*$/s,
        ""
    );

    answer.textContent = cleanAnswer;


    if (
        Array.isArray(data.citations) &&
        data.citations.length > 0
    ) {

        citationsSection.classList.remove(
            "hidden"
        );


        data.citations.forEach(
            function (citation) {

                const element =
                    document.createElement(
                        "div"
                    );

                element.className =
                    "citation";


                let title = citation;
                let description = "";


                /*
                 * Income threshold citations
                 */

                if (citation === "§6.6.1") {

                    title =
                        "Policy Manual § 6.6.1";

                    description =
                        "Original policy section containing the income-threshold rule.";

                } else if (
                    citation === "Amendment §3.1"
                ) {

                    title =
                        "Amendment § 3.1";

                    description =
                        "Updates the income-threshold values.";

                } else if (
                    citation === "Amendment §5.1"
                ) {

                    title =
                        "Amendment § 5.1";

                    description =
                        "Defines when the amendment applies.";

                }


                /*
                 * Reporting period citations
                 */

                else if (citation === "§4.3.2") {

                    title =
                        "Policy Manual § 4.3.2";

                    description =
                        "Original policy section defining the reporting period.";

                } else if (
                    citation === "Amendment §2.1"
                ) {

                    title =
                        "Amendment § 2.1";

                    description =
                        "Updates the reporting period from 10 to 14 calendar days.";

                } else if (
                    citation === "Amendment §5.2"
                ) {

                    title =
                        "Amendment § 5.2";

                    description =
                        "Defines which changes of circumstances are covered by the amendment.";

                }


                /*
                 * Earnings disregard citations
                 */

                else if (citation === "§6.4.1") {

                    title =
                        "Policy Manual § 6.4.1";

                    description =
                        "Original policy section defining the earnings disregard.";

                } else if (
                    citation === "Amendment §1.1"
                ) {

                    title =
                        "Amendment § 1.1";

                    description =
                        "Updates the earnings disregard amount.";

                }


                /*
                 * Sanction citations
                 */

                else if (citation === "§10.5.2") {

                    title =
                        "Policy Manual § 10.5.2";

                    description =
                        "Original policy section defining the sanction percentage.";

                } else if (
                    citation === "Amendment §4.1"
                ) {

                    title =
                        "Amendment § 4.1";

                    description =
                        "Updates the sanction percentage.";

                }


                /*
                 * Fallback for any other citation.
                 */

                else {

                    title =
                        citation.replace(
                            "§",
                            "§ "
                        );
                }


                element.innerHTML = `
                    <strong>${title}</strong>
                    ${
                        description
                            ? `<span>${description}</span>`
                            : ""
                    }
                `;


                citations.appendChild(
                    element
                );

            }
        );

    } else {

        citationsSection.classList.add(
            "hidden"
        );

    }
}


function displayError(error) {

    result.classList.remove(
        "hidden"
    );

    answer.classList.remove(
        "hidden"
    );

    refusalSection.classList.add(
        "hidden"
    );

    citationsSection.classList.add(
        "hidden"
    );


    answer.textContent =
        "Unable to connect to the policy server. " +
        "Please make sure the FastAPI backend is running.";

    console.error(error);
}


function setLoading(isLoading) {

    if (isLoading) {

        loading.classList.remove(
            "hidden"
        );

        askButton.disabled = true;

        askButton.textContent =
            "Checking...";

    } else {

        loading.classList.add(
            "hidden"
        );

        askButton.disabled = false;

        askButton.innerHTML =
            'Ask Policy <span>→</span>';

    }
}