root = exports ? this

to_2digit=(i)->
    if i>=10 then i.toString() else "0"+i.toString()

root.get_blanks_random = (question) ->
    phrases=question.split("/")
    output_string=""
    for i in [0..phrases.length-1]
        phrase=phrases[i]
        output_string+=(if Math.random()<0.4 then phrase else "<div class='form-group'><input type='text' class='form-control' name='input#{to_2digit(i)}' maxlength='#{phrase.length-1}'></div>#{phrase.slice(-1)}")
    output_string

root.check_answer_random=(question)->
    phrases=question.split("/")
    inputs=document.getElementsByTagName("input")
    for i in [0..inputs.length-1]
        input=inputs[0]
        index=parseInt(input.getAttribute("name").slice(-2))
        correct=phrases[index].slice(0,-1)
        input.parentNode.innerHTML=(if input.value is correct then "<font color='green'>#{correct}</font>" else "<font color='red'>#{correct}</font>")

    document.getElementById("submit").innerHTML="下一题"
    if $.cookie("gseq") and $.cookie("qseq")
        $.cookie("qseq",parseInt($.cookie("qseq")) + 1)
    document.getElementById("submit").onclick=()->location.reload()

root.get_blanks_strict=(question,answer)->
    question_split=question.split("###")
    output_string=""
    for i in [0..question_split.length-2]
        output_string+=question_split[i]
        output_string+="<div class='form-group'><input type='text' class='form-control' name='input#{i}' maxlength='#{answer[i].length}'></div>"
    output_string+=question_split[question_split.length-1]

root.check_answer_strict=(answer)->
    inputs=document.getElementsByTagName("input")
    for i in [0..answer.length-1]
        input=inputs[0]
        correct=answer[i]
        input.parentNode.innerHTML=(if input.value is correct then "<font color='green'>#{correct}</font>" else "<font color='red'>#{correct}</font>")
    document.getElementById("submit").innerHTML="下一题"
    if $.cookie("gseq") and $.cookie("qseq")
        $.cookie("qseq",parseInt($.cookie("qseq")) + 1)
    document.getElementById("submit").onclick=()->location.reload()
