root = exports ? this
root.get_random_blanks = (question) ->
    phrases=question.split("/")
    blank_chosen=[]
    num_blanks=Math.floor(phrases.length*0.6)
    loop
        index=Math.floor(Math.random()*phrases.length)
        blank_chosen.push(index) if index not in blank_chosen
        break if blank_chosen.length==num_blanks
    output_string=""
    output_string+=(if i not in blank_chosen then phrases[i] else "<div class=\"form-group\"><input type=\"text\" class=\"form-control\" name=\"input#{i}\" maxlength=\"#{phrases[i].length-1}\"></div>#{phrases[i].slice(-1)}") for i in [0..phrases.length-1]
    output_string

root.check_answer=(question)->
    phrases=question.split("/")
    inputs=document.getElementsByTagName("input")
    inputs[0].parentNode.innerHTML=(if inputs[0].value is phrases[inputs[0].getAttribute("name").slice(-1)].slice(0,-1) then "<font color='green'>#{phrases[inputs[0].getAttribute("name").slice(-1)].slice(0,-1)}</font>" else "<font color='red'>#{phrases[inputs[0].getAttribute("name").slice(-1)].slice(0,-1)}</font>") for i in [0..inputs.length-1]
    document.getElementById("submit").innerHTML="下一题"
    if $.cookie("gseq") and $.cookie("qseq")
        $.cookie("qseq",parseInt($.cookie("qseq")) + 1)
    document.getElementById("submit").onclick=()->location.reload()
