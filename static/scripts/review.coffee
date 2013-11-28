root = exports ? this
root.get_random_blanks = (question) ->
    to_2digit=(i)->
        if i>=10 then i.toString() else "0"+i.toString()
    phrases=question.split("/")
    output_string=""
    for i in [0..phrases.length-1]
        phrase=phrases[i]
        output_string+=(if Math.random()<0.4 then phrase else "<div class=\"form-group\"><input type=\"text\" class=\"form-control\" name=\"input#{to_2digit(i)}\" maxlength=\"#{phrase.length-1}\"></div>#{phrase.slice(-1)}")
    output_string

root.check_answer=(question)->
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
