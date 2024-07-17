CUSTOM_CARD_MODEL_NAME = "custom_card"

CUSTOM_CARD_FIELDS = ["Expression", "Meaning", "Pronunciation", "Sentence"]

CUSTOM_CARD_CSS = """
/* General card styles */
.card {
    text-align: center;
    color: #333333;
    background-color: #f5f5f5;
    word-wrap: break-word;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    max-height: 100%;
    max-width: 100%;
    box-sizing: border-box;
}

@media screen and (max-width: 480px) {
    .card {
        font-size: 18px;
    }
}

/* Front side */
.front-container {
    display: flex;
    justify-content: center;
    align-items: center;
    max-height: 100%;
    max-width: 100%;
    padding: 20px;
}

/* Back side */
.back-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    max-height: 100%;
    max-width: 100%;
}

.big {
    font-size: 2.5em; /* Adjust size as needed */
}

.definition, .pronunciation {
    font-size: 20px;
    text-align: left;
    max-width: 500px;
}

.example {
    font-size: 18px;
    text-align: left;
    max-width: 500px;
}

.example a {
    color: #4a90e2;
    text-decoration: underline;
}

.example a:hover {
    color: #0f7dda;
    cursor: pointer;
}

/* Night mode styles */
.night_mode {
    background-color: #212121;
    color: #f5f5f5;
}

/* Expression styles */
.hiddenfuri ruby, .hiddenfuri > span, .hiddenfuri > b > span {
    /* Hide Expression by default */
    visibility: hidden;
}

.hiddenfuri.show ruby, .hiddenfuri.show > span, .hiddenfuri.show > b > span {
    /* Show Expression on hover or touch */
    visibility: visible;
}
"""

CUSTOM_CARD_FRONT_HTML = """
<div class="front-container">
    <div class="big Expression-container">{{Expression:Expression}}</div>
</div>

<script>
$(document).ready(function() {
    $('.Expression-container rt').css('visibility', 'hidden'); // Hide Expression initially

    $('.Expression-container').on('mouseover touchstart', function(e) {
        // Show Expression on hover or touch
        $(this).find('rt').css('visibility', 'visible');
    });

    $('.Expression-container').on('mouseout touchend', function(e) {
        // Re-hide Expression when not hovering or touching
        $(this).find('rt').css('visibility', 'hidden');
    });
});
</script>
"""

CUSTOM_CARD_BACK_HTML = """
<div class="back-container">
   <div class="big">{{Expression:Expression}}</div>
    <div class="definition">
        <span class="label">定義：</span>{{Meaning}}
    </div>
    <div class="pronunciation">
        <span class="label">発音：</span>{{Pronunciation}}
    </div>
    <div class="example">
        <a href="#" class="example-link" onclick="document.getElementById('hint').style.display='block';return false;"><span class="label">例文：</span></a>
        <div id="hint" class="example-text" style="display: none">{{Sentence}}</div>
    </div>
</div>
"""

CUSTOM_CARD_TEMPLATES = [
    {
        "Name": "My Card 1",
        "Front": CUSTOM_CARD_FRONT_HTML,
        "Back": CUSTOM_CARD_BACK_HTML
    }
]
