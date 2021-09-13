
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
let csrftoken = getCookie('csrftoken');

let ques_container_height = document.querySelector(".page_container");
let block = document.createElement("div");
block.style.height = `90px`;
block.style.width = "300px";
ques_container_height.appendChild(block);

// const markdown_button = document.getElementById("md_helpbox");
// const cancel = document.querySelector("#cancel_md");
//
// markdown_button.addEventListener("click", function(event) {
//   let markdown_menu = document.querySelector(".markdown_helper");
//   markdown_menu.classList.toggle("hide")
// })
//
// cancel.addEventListener("click", function(event) {
//   let markdown_menu = document.querySelector(".markdown_helper");
//   markdown_menu.classList.toggle("hide")
// })

var headers = new Headers({
  "Accept": "application/json",
  "Content-Type": "application/json",
  "X-CSRFToken": csrftoken
});

function parseJson(response) {
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

let question_vote_buttons = document.querySelectorAll(".question_vote");
question_vote_buttons.forEach(function(vote_button) {
  vote_button.addEventListener("click", function(event) {
    let voted_post = this.id.split("_");
    let _question = voted_post[0];
    let q_id = _question.match(/\d+$/)[0];
    let vote = voted_post[1];

    const request = new Request(
      `http://localhost:8000/api/v1/questions/${q_id}/`, {
        "method": "put",
        "headers": headers,
        "body": JSON.stringify({
          "vote": vote
        })
      }
    );

    function pop_warning(element) {
      element.classList.add("hide_error");
      element.classList.remove("show_error");
      element.parentElement.removeChild(element);
    }

    fetch(request).then(parseJson).then((response) => {
      if (!response.ok) {
        message = response.json['vote'];
        console.log(message);
        throw new Error(message)
      } else {
        console.log("here");
        const question = document.getElementById(`question${q_id}_tally`);
        question.textContent = response.json['tally'];

      }
    }).catch((error) => {
      console.log("Wrong");
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
        delete_message.classList.add("delete_message")
        delete_message.innerText = "The question you posted is now deleted";
        deleted_div.appendChild(delete_message);
        deleted_div.classList.add("deleted");
        let body = document.querySelector("body");
        body.appendChild(deleted_div);
        setTimeout(function() {
          window.location.replace("http://localhost:8000/")
        }, 2000)
      }
    })
  })
})

let answer_vote_buttons = document.querySelectorAll(".answer_vote");
answer_vote_buttons.forEach(function(vote_button) {
  vote_button.addEventListener("click", function(event) {
    const question_answer = this.id;
    let [question_id, answer_id] = Array.from(question_answer.matchAll(/(?<=\w+)\d+/g));
    var answer_vote = question_answer.split("__")[1];
    const [answer, vote] = answer_vote.split("_")

    const request = new Request(
      `http://localhost:8000/api/v1/questions/${question_id}/answers/${answer_id}/`, {
        'method': 'put',
        'headers': headers,
        'body': JSON.stringify({
          "vote": vote
        })
      }
    );

    fetch(request).then(parseJson).then((response) => {
      if (!response.ok) {
        var message;
        if (response.status_code == 429) {
          message = response.json['detail'];
        } else {
          message = response.json['vote'];
        }
        throw new Error(message);
      } else {
        const total_votes = response.json['tally'];
        const answer_vote_points = document.getElementById(`answer${answer_id}_tally`);
        answer_vote_points.textContent = total_votes;
      }

    }).catch((e) => {
      const element = this.getBoundingClientRect();
      let body = document.querySelector("body");
      let error_message = document.createElement('p');
      error_message.id = "error_message";
      error_message.textContent = e.message;
      if (question_answer.endsWith("upvote")) {
        error_message.style.cssText = `position: absolute; left: ${element.left + 20}px; top: ${element.top - 45}px; background: blue`;
      } else {
        error_message.style.cssText = `position: absolute; left: ${element.left + 25}px; top: ${element.top - 25}px; background: blue`;
      }
      body.appendChild(error_message);
      this.addEventListener("mouseout", function(event) {
        const message = document.getElementById("error_message");
        message.remove();
      }, {'once': true})
    })
  })

  let posted_question_answers = document.querySelectorAll(".delete_answer");
  posted_question_answers.forEach((answer) => {
    answer.addEventListener("click", function(event) {
      event.stopImmediatePropagation();
      const question_answer = this.id;
      let [question_id, answer_id] = Array.from(question_answer.matchAll(/(?<=\w+)\d+/g));
      var answer_vote = question_answer.split("__")[1];
      const [answer, vote] = answer_vote.split("_")

      const request = new Request(
        `http://localhost:8000/api/v1/questions/${question_id}/answers/${answer_id}/`, {
          'method': 'delete',
          'headers': headers
        }
      );
      fetch(request).then((response) => {
        this.parentElement.parentElement.parentElement.parentElement.remove();
        let answer_count = document.getElementById("answer_count");
        const n = parseInt(answer_count.textContent[0]) - 1;
        let answers;
        if (n > 1 || n == 0) {
          answers =  ` answers`;
        } else {
          answers = ` answer`;
        }
        answer_count.textContent = `${n} ${answers}`
      })
    })
  })

  document.addEventListener("scroll", function(event) {
    let pixelScroll = window.scrollY;
    let search_form_input = document.querySelector("#search_form");
    // if (pixelScroll >= 80) {
    //   search_form_input.classList.add("hide_form");
    //   console.dir(search_form_input);
    // } else {
    //     search_form_input.classList.remove("hide_form");
    // }
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
