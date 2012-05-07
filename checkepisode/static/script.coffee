$(document.body).on 'click', '.comment', (e) ->
  target = $(e.target)
  console.log target

  if target.hasClass 'edit'
    editClicked $(this)
    e.preventDefault()
  else if target.hasClass 'delete'
    deleteClicked $(this)
    e.preventDefault()

$(document.body).on 'click', '.alert:not(.modal)', (e) ->
  if not $(e.target).hasClass 'btn'
    $(this).slideUp()

$('#add-comment').on 'submit', 'form', (e) ->
  $(this).find('input[name="token"]').val getToken()

  $.ajax
    type: 'POST'
    url: $(this).attr 'action'
    data: $(this).serialize()
    dataType: 'json'
    success: (data) =>
      if data.status is 'success'
        $(this).find('input[type="text"], textarea').val ''
        renderComment data.id
      else
        showMessage data.message

      console.log 'token', data.token
      setToken data.token
    error: (data) ->
      showMessage "#{data.status}: #{data.statusText}"

  e.preventDefault()

renderComment = (id) ->
  $.get "/comments/#{id}", (data) ->
    $(data).insertBefore($('#add-comment')).hide().slideDown()

templates = {}
templateUrls =
  message: '/static/templates/message.html'
  delete: '/static/templates/delete-comment.html'

_.templateSettings =
  interpolate: /\{\{(.+?)\}\}/g

getTemplate = (name, cb) ->
  if templates[name]
    return cb()

  $.get templateUrls[name], (data) ->
    templates[name] = _.template data
    cb()

getToken = -> $(document.body).data 'token'
setToken = (token) -> $(document.body).data 'token', token

getCommentData = (comment) ->
  username: comment.find '.anonymous'
  content: comment.find '.content'
  url: comment.find('.edit').attr 'href'
  deleteUrl: comment.find('.delete').attr 'href'

setCommentData = (comment, data) ->
  if data.username?
    comment.data.username.text data.username
  if data.content?
    comment.data.content.text data.content

hideComment = (comment) ->
  comment.find('.anonymous, .content, .comment-controls a').hide()

showComment = (comment) ->
  comment.find('.anonymous, .content, .comment-controls a').show()

showMessage = null
do ->
  gmodal = null
  showMessage = (message, level='error', cb=null) ->
    getTemplate 'message', ->
      gmodal?.modal('hide').remove()
      gmodal = $(templates.message message: message, level: level)
      $(document.body).append gmodal
      gmodal.modal()
      cb?(gmodal)

saveEdit = (button, comment) ->
  button.attr 'disabled', 'disabled'

  username = comment.data.new_username.val().trim()
  content = comment.data.new_content.val().trim()
  token = getToken()

  comment.data.xhr = $.ajax
    type: 'POST'
    url: comment.data.url
    data: "username=#{username}&content=#{content}&token=#{token}"
    dataType: 'json'
    success: (data) ->
      if data.status is 'success'
        setCommentData comment, username: username, content: content
        hideEditForm comment
        showComment comment
      else
        showMessage '<strong>Error!</strong> ' + data.message
        button.removeAttr 'disabled'

      setToken data.token

discardEdit = (comment) ->
  comment.data.xhr?.abort()
  hideEditForm comment
  showComment comment

createEditButtons = (comment) ->
  save = $('<button class="btn btn-primary">').text 'Save'
  cancel = $('<button class="btn">').text 'Cancel'

  save.on 'click', -> saveEdit $(this), comment
  cancel.on 'click', -> discardEdit comment

  [save, cancel]

hideEditForm = (comment) ->
  comment.find('.edit-username, .edit-content, .comment-controls button')
    .remove()

showEditForm = (comment) ->
  data = comment.data
  if data.username
    nameField = $('<input class="edit-username">').val data.username.text()
      .trim()
    data.new_username = nameField
    data.username.after nameField

  contentField = $('<textarea class="edit-content span11">')
    .val data.content.text().trim()
  data.new_content = contentField
  data.content.after contentField

  [save, cancel] = createEditButtons comment
  controls = comment.find '.comment-controls'
  controls.append save
  controls.append cancel

editClicked = (comment) ->
  comment.data = getCommentData comment
  hideComment comment
  showEditForm comment

deleteComment = (comment, modal) ->
  token = getToken()

  $.ajax
    type: 'POST'
    url: comment.data.deleteUrl
    data: "token=#{token}&action=delete"
    dataType: 'json'
    success: (data) ->
      if data.status is 'success'
        comment.slideUp()
        modal.modal 'hide'
      else
        showMessage "<strong>Error!</strong> #{data.message}"

      setToken data.token
    error: (data) ->
      showMessage "#{data.status}: #{data.statusText}"

deleteClicked = (comment) ->
  comment.data = getCommentData comment
  getTemplate 'delete', ->
    showMessage templates.delete(), 'danger', (modal) ->
      modal.on 'click', '.delete', ->
        deleteComment comment, modal
      modal.on 'click', '.cancel', ->
        console.log 'click'
        modal.modal 'hide'
