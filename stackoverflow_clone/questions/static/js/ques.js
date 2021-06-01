
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


const markdown_button = document.getElementById("md_helpbox");
const cancel = document.querySelector("#cancel_md");

markdown_button.addEventListener("click", function(event) {
  let markdown_menu = document.querySelector(".markdown_helper");
  markdown_menu.classList.toggle("hide")
})

cancel.addEventListener("click", function(event) {
  let markdown_menu = document.querySelector(".markdown_helper");
  markdown_menu.classList.toggle("hide")
})

const headers = new Headers({
  "Accept": "application/json",
  "Content-Type": "application/json",
  "X-CSRFToken": csrftoken
});


let question_vote_buttons = document.querySelectorAll(".question_vote");
question_vote_buttons.forEach(function(vote_button) {
  vote_button.addEventListener("click", function(event) {
    voted_post = this.id.split("_")
    const _question = voted_post[0];
    q_id = _question.match(/\d+$/)[0];
    vote = voted_post[1]

    const request = new Request(
      `http://localhost:8000/api/v1/questions/${q_id}/`, {
        "method": "put",
        "headers": headers,
        "body": JSON.stringify({
          "vote": vote
        })
      }
    );

    function parseJson(response) {
      // debugger;
      return new Promise((resolve) => {
        return response.json().then((json) => {
          resolve({
            'status_code': response.status,
            'ok': response.ok,
            'json': json
          })
        })
      })
    }

    function pop_warning(element) {
      element.classList.add("hide_error");
      element.classList.remove("show_error");
      element.parentElement.removeChild(element);
    }

    fetch(request).then(parseJson).then((response) => {
      if (!response.ok) {
        message = response.json['vote']
        console.log(response.json)
        throw new Error(message)
      }
    }).catch((error) => {
      let vote_error = document.createElement("p");
      vote_error.classList.add("show_error");
      vote_error.textContent = error.message;
      let centered_div = document.querySelector(".centered");
      centered_div.insertBefore(vote_error, centered_div.firstElementChild);
      setTimeout(pop_warning, 2250, vote_error)
    })
  })
})

let delete_question_buttons = document.querySelectorAll(".delete_question");
delete_question_buttons.forEach((button) => {
  button.addEventListener("click", function(event) {
    const [method, question] = this.id.split("_");
    const question_id = question.match(/\d+$/)[0];
    console.log(question_id);

    const request = new Request(
      `http://localhost:8000/api/v1/questions/`, {
        'method': method,
        'headers': headers,
        'body': JSON.stringify({
          'id': question_id
        })
      }
    );

    fetch(request).then((response) => {
      if (response.ok) {
        let deleted_div = document.createElement("div");
        let delete_message = document.createElement('p');
        p.innerText = "The question you posted is now deleted";
        deleted_div.appendChild(delete_message);
        deleted_div.classList.add("deleted");
        let body = document.querySelector("body");
        body.appendChild(deleted_div);
      }
    })
  })
})


// parsed_json = response.json()
// if (response.status === 200) {
//   return parsed_json
// } else {
//   const message = parsed_json['vote'];
//   throw new Error(message);
// }

// .then((data) => {
//   let vote_tally = document.getElementById(`question${q_id}_tally`);
//   vote_tally.textContent = data['tally']
// })
