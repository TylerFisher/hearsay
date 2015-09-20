var $shareQuote;
var $modal;
var $shareModal;
var $shareBtn;
var currentQuote;
var currentId;

/*
 * Run on page load.
 */
var onDocumentLoad = function(e) {
    $shareQuote = $('.share-quote');
    $introModal = $('#intro-modal');
    $shareModal = $('#share-modal');
    $shareBtn = $('.btn-share');

    if (ACCESS_TOKEN) {
        $shareQuote.on('click', onShareQuoteClick);
        $shareQuote.popover({
            html: true,
            placement: 'top'
        });
    } else {
        $introModal.modal();
    }

    $('body').on('click', '.share', onShareClick);
    $shareModal.on('show.bs.modal', onShareModalShow);
    $shareBtn.on('click', onShareBtnClick);
}

var onShareQuoteClick = function(e) {
    e.preventDefault();
    currentQuote = $(this).text();
    currentId = $(this).data('id');
}

var onShareClick = function() {
    $shareModal.modal();
}

var onShareModalShow = function() {
    var $modal = $(this);
    $modal.find('.modal-body video').attr('src', 'http://127.0.0.1:8000/assets/' + currentId + '.mp4');
    $modal.find('.modal-body textarea').text(currentQuote + ' #audiohack');
}

var onShareBtnClick = function(e) {
    e.preventDefault();
    var text = $('textarea').val();
    var url = 'http://127.0.0.1:8001/hearsay/post_video/?token=' + ACCESS_TOKEN + '&secret=' + ACCESS_SECRET + '&vid_id=' + currentId + '&tweet=' + escape(text);
    $.post(url, function(data) {
        $shareModal.modal();
    });
}

$(onDocumentLoad);
