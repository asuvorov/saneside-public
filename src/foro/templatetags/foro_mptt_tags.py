from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


register = template.Library()


class RecurseTreeNode(template.Node):
    """Docstring."""

    def __init__(self, template_nodes, queryset_var):
        self.template_nodes = template_nodes
        self.queryset_var = queryset_var

    def _render_node(self, context, node):
        """Docstring."""
        bits = []
        context.push()

        for child in node.children.all():
            bits.append(self._render_node(context, child))

        context["node"] = node
        context["children"] = mark_safe("".join(bits))

        rendered = self.template_nodes.render(context)

        context.pop()

        return rendered

    def render(self, context):
        """Docstring."""
        queryset = self.queryset_var.resolve(context)

        bits = [self._render_node(context, node) for node in queryset]

        return "".join(bits)


@register.tag
def recursetree(parser, token):
    """Iterate over the Nodes in the Tree.

    Renders the contained Block for each Node.
    This Tag will recursively render Children into the Template Variable
    {{ children }}.

    Usage:
        <ul>
        {% recursetree nodes %}
            <li>
                {{ node.name }}

            {% if not node.is_leaf_node %}
                <ul>
                    {{ children }}
                </ul>
            {% endif %}
            </li>
        {% endrecursetree %}
        </ul>
    """
    bits = token.contents.split()

    if len(bits) != 2:
        raise template.TemplateSyntaxError(
            _("%s Tag requires a QuerySet") % bits[0])

    queryset_var = template.Variable(bits[1])

    template_nodes = parser.parse(("endrecursetree",))
    parser.delete_first_token()

    return RecurseTreeNode(template_nodes, queryset_var)
